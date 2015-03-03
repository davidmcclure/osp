

from osp.common.config import config
from osp.common.models.base import BaseModel
from osp.corpus.corpus import Corpus
from osp.corpus.syllabus import Syllabus
from playhouse.postgres_ext import BinaryJSONField
from peewee import *


class Document(BaseModel):


    path = CharField(unique=True)
    metadata = BinaryJSONField(null=True)


    @classmethod
    def insert_documents(cls, corpus):

        """
        Insert a document row for each syllabus in the corpus.

        Args:
            corpus (Corpus): A corpus instance.
        """

        for segment in corpus.segments():

            rows = []
            for syllabus in segment.syllabi():
                rows.append({'path': syllabus.relative_path})

            # Bulk-insert the segment.
            with cls._meta.database.transaction():
                cls.insert_many(rows).execute()


    @property
    def syllabus(self):

        """
        Wrap the row as an OSP Syllabus instance.
        """

        return Syllabus.from_env(self.path)


    class Meta:
        database = config.get_table_db('document')
