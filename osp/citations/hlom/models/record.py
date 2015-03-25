

import sys
import spacy.en
import numpy as np
import hashlib

from osp.common.config import config
from osp.common.models.base import BaseModel
from osp.citations.hlom.utils import prettify_field
from osp.citations.hlom.dataset import Dataset
from pymarc import Record
from scipy.stats import rankdata
from playhouse.postgres_ext import *
from peewee import *


# Load spaCy.
# nlp = spacy.en.English()


class HLOM_Record(BaseModel):


    control_number = CharField(unique=True, null=False)
    record = BlobField(null=False)
    metadata = BinaryJSONField(default={})


    class Meta:
        database = config.get_table_db('hlom_record')


    @classmethod
    def insert_records(cls, page_size=10000):

        """
        Insert an row for each record in the HLOM corpus.

        Args:
            page_size (int): Batch-insert page size.
        """

        dataset = Dataset.from_env()

        i = 0
        for group in dataset.grouped_records(page_size):

            rows = []
            for record in group:

                # Require title and author.
                if record and record.title() and record.author():

                    rows.append({
                        'control_number': record['001'].format_field(),
                        'record': record.as_marc()
                    })

            if rows:
                HLOM_Record.insert_many(rows).execute()

            i += 1
            sys.stdout.write('\r'+str(page_size*i))
            sys.stdout.flush()


    @property
    def pymarc(self):

        """
        Wrap the raw record blob as a Pymarc record instance.
        """

        return Record(
            data=bytes(self.record),
            ascii_handling='ignore',
            utf8_handling='ignore'
        )


    @property
    def hash(self):

        """
        Create a deduping hash for the record that tries to coalesce
        differently-formatted editions of the same text.
        """

        text = ' '.join([
            self.pymarc.title(),
            self.pymarc.author()
        ])

        tokens = nlp(text.lower())

        # Filter out articles / punctuation.
        tokens = [t.orth_ for t in tokens if
                  t.pos_ not in ['DET', 'PUNCT'] and
                  t.orth_.strip()]

        # Ignore order.
        tokens.sort()

        # Hash the filtered tokens.
        sha1 = hashlib.sha1()
        sha1.update(' '.join(tokens).encode('ascii', 'ignore'))
        return sha1.hexdigest()


    # Denormalization routines for Elasticsearch.
    # TODO: How to do this dynamically?


    @property
    def es_doc(self):

        """
        Construct a document for Elasticsearch.

        Returns:
            dict: The document fields.
        """

        return {
            '_id':          self.control_number,
            'author':       prettify_field(self.pymarc.author()),
            'title':        prettify_field(self.pymarc.title()),
            'publisher':    prettify_field(self.pymarc.publisher()),
            'pubyear':      prettify_field(self.pymarc.pubyear()),
            'count':        self.metadata['citation_count'],
            'rank':         self.metadata['teaching_rank'],
            'percent':      self.metadata['teaching_percent']
        }


    @classmethod
    def blacklist(cls, control_number):

        """
        Exclude a record from indexing.

        Args:
            control_number (str)
        """

        record = cls.get(cls.control_number==control_number)
        record.metadata['blacklisted'] = True
        record.save()


    @classmethod
    def select_cited(cls):

        """
        Select records that aren't blacklisted.
        """

        return (

            cls.select()

            # Omit blacklisted records.
            .where(~cls.metadata.contains('blacklisted'))

            # Omit records with no citations.
            .where(cls.metadata.contains('citation_count'))

            # Coalesce duplicates.
            .distinct([cls.metadata['deduping_hash']])
            .order_by(
                cls.metadata['deduping_hash'],
                cls.id
            )

        )


    @classmethod
    def write_citation_count(cls):

        """
        Cache citation counts.
        """

        from osp.citations.hlom.models.citation import HLOM_Citation

        for pair in HLOM_Citation.text_counts():

            # Write on the citation count.
            pair.record.metadata['citation_count'] = pair.count
            pair.record.save()


    @classmethod
    def write_deduping_hash(cls):

        """
        Cache deduping hashes.
        """

        query = cls.select().where(
            cls.metadata.contains('citation_count')
        )

        for row in query:
            row.metadata['deduping_hash'] = row.hash
            row.save()


    @classmethod
    def write_teaching_rank(cls):

        """
        Cache teaching ranks and percentiles.
        """

        # Get record -> count tuples.
        records = list(cls.select_cited())

        # Get min/max ranks.
        counts = [r.metadata['citation_count'] for r in records]
        max_ranks = rankdata(counts, 'max')
        min_ranks = rankdata(counts, 'min')

        # Rank in ascending order.
        max_ranks = max_ranks.max()+1 - max_ranks
        min_ranks = min_ranks.max()+1 - min_ranks
        log_count = np.log(len(records))

        for i, record in enumerate(records):

            max_rank = int(max_ranks[i])
            min_rank = int(min_ranks[i])

            # Get the log ratio of the rank.
            percent = ((log_count-np.log(min_rank))/log_count)*100

            record.metadata['teaching_rank'] = max_rank
            record.metadata['teaching_percent'] = percent
            record.save()
