

from osp.common.config import config
from osp.corpus.models.text import Document_Text
from elasticsearch.helpers import bulk
from playhouse.postgres_ext import ServerSide


class CorpusIndex:


    def __init__(self):

        """
        Set the Elasticsearch connection.
        """

        self.es = config.get_es()


    def create(self):

        """
        Set the Elasticsearch mapping.
        """

        self.es.indices.create('osp', {
            'mappings': {
                'syllabus': {
                    '_id': {
                        'index': 'not_analyzed',
                        'store': True
                    },
                    'properties': {
                        'body': {
                            'type': 'string'
                        }
                    }
                }
            }
        })


    def index(self):

        """
        Insert documents.
        """

        def stream():
            for row in ServerSide(Document_Text.select()):
                yield row.es_doc

        # Batch-insert the documents.
        bulk(self.es, stream(), index='osp', doc_type='syllabus')

        # Commit the index.
        self.es.indices.flush('osp')


    def delete(self):

        """
        Delete the index.
        """

        if self.es.indices.exists('osp'):
            self.es.indices.delete('osp')


    def count(self):

        """
        Count the number of documents.

        Returns:
            int: The number of docs.
        """

        return self.es.count('osp', 'syllabus')['count']


    def reset(self):

        """
        Clear and recreate the index.
        """

        self.delete()
        self.create()
