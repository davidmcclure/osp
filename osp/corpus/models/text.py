

from osp.common.config import config
from osp.common.models.base import BaseModel
from osp.common.models.elasticsearch import ElasticsearchModel
from osp.corpus.models.document import Document
from peewee import *


class Document_Text(BaseModel, ElasticsearchModel):


    document = ForeignKeyField(Document, unique=True)
    text = TextField()


    class Meta:
        database = config.get_table_db('document_text')


    es_index = 'osp'
    es_doc_type = 'syllabus'


    es_mapping = {
        '_id': {
            'index': 'not_analyzed',
            'store': True
        },
        'properties': {
            'doc_id': {
                'type': 'integer'
            },
            'body': {
                'type': 'string'
            }
        }
    }


    @classmethod
    def es_stream_docs(cls):

        """
        Index all texts.

        Yields:
            dict: The next document.
        """

        for row in cls.select():
            yield row.es_doc


    @property
    def es_doc(self):

        """
        Construct a document for Elasticsearch.

        Returns:
            dict: The document fields.
        """

        return {
            '_id':      self.document.path,
            'doc_id':   self.document.id,
            'body':     self.text
        }
