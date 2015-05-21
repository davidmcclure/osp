

import sys
import re
import numpy as np
import hashlib

from osp.common.config import config
from osp.common.utils import query_bar
from osp.common.models.base import BaseModel
from osp.common.mixins.elasticsearch import Elasticsearch
from osp.citations.hlom.utils import prettify_field
from osp.citations.hlom.dataset import Dataset
from osp.citations.hlom.utils import sanitize_query
from osp.citations.hlom.marc import MARC
from scipy.stats import rankdata
from clint.textui.progress import bar
from playhouse.postgres_ext import *
from peewee import *


class HLOM_Record(BaseModel, Elasticsearch):


    control_number = CharField(unique=True, null=False)
    record = BlobField(null=False)
    metadata = BinaryJSONField(default={})


    class Meta:
        database = config.get_table_db('hlom_record')


    es_index = 'hlom'
    es_doc_type = 'record'


    es_mapping = {
        '_id': {
            'index': 'not_analyzed',
            'store': True
        },
        'properties': {
            'author': {
                'type': 'string'
            },
            'title': {
                'type': 'string'
            },
            'publisher': {
                'type': 'string'
            },
            'pubyear': {
                'type': 'string'
            },
            'count': {
                'type': 'integer'
            },
            'rank': {
                'type': 'integer'
            },
            'score': {
                'type': 'float'
            },
        }
    }


    @classmethod
    def es_stream_docs(cls):

        """
        Just index cited rows.

        Yields:
            dict: The next document.
        """

        for row in cls.select_cited():
            yield row.es_doc


    @property
    def es_doc(self):

        """
        Construct a document for Elasticsearch.

        Returns:
            dict: The document fields.
        """

        return {
            '_id':              self.control_number,
            'author':           prettify_field(self.marc.author()),
            'title':            prettify_field(self.marc.title()),
            'publisher':        prettify_field(self.marc.publisher()),
            'pubyear':          prettify_field(self.marc.pubyear()),
            'count':            self.metadata['citation_count'],
            'rank':             self.metadata['rank'],
            'score':            self.metadata['score'],
        }


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
    def marc(self):

        """
        Wrap the MARC blob as a Pymarc instance.

        Returns:
            pymarc.Record
        """

        return MARC(
            data=bytes(self.record),
            ascii_handling='ignore',
            utf8_handling='ignore'
        )


    @property
    def hash(self):

        """
        Create a hash that tries to merge together differently-formatted
        editions of the same text.

        Returns:
            str: The deduping hash.
        """

        # Get "[title] [author]".
        text = ' '.join([
            self.marc.title(),
            self.marc.author()
        ])

        # Lowercase, tokenize, sort tokens.
        tokens = sorted(re.findall('\w+', text.lower()))

        # Remove articles.
        tokens = [t for t in tokens if t not in ['a', 'an', 'the']]

        # Hash the filtered tokens.
        sha1 = hashlib.sha1()
        sha1.update(' '.join(tokens).encode('ascii', 'ignore'))
        return sha1.hexdigest()


    @property
    def query(self):

        """
        Build an Elasticsearch query string.

        Returns:
            str: "[title] [author]"
        """

        return sanitize_query(' '.join([
            self.marc.title(),
            self.marc.author()
        ]))
