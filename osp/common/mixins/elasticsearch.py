

from osp.common.config import config
from elasticsearch.client import _make_path
from elasticsearch.helpers import bulk


class Elasticsearch:


    @property
    def es_mapping(self):
        raise NotImplementedError


    @property
    def es_doc(self):
        raise NotImplementedError


    @classmethod
    def es_stream_docs(cls):
        raise NotImplementedError


    @property
    def es_index(self):
        raise NotImplementedError


    @property
    def es_doc_type(self):
        raise NotImplementedError


    @classmethod
    def es_create(cls):

        """
        Set the Elasticsearch mapping.
        """

        config.es.indices.create(cls.es_index, {
            'mappings': { cls.es_doc_type: cls.es_mapping }
        })


    @classmethod
    def es_delete(cls):

        """
        Delete the index.
        """

        if config.es.indices.exists(cls.es_index):
            config.es.indices.delete(cls.es_index)


    @classmethod
    def es_insert(cls, *args, **kwargs):

        """
        Insert documents.
        """

        # Batch-insert the documents.
        bulk(
            config.es,
            cls.es_stream_docs(*args, **kwargs),
            raise_on_exception=False,
            doc_type=cls.es_doc_type,
            index=cls.es_index
        )

        # Commit the index.
        config.es.indices.flush(cls.es_index)


    @classmethod
    def es_count(cls):

        """
        Count the number of documents.

        Returns:
            int: The number of docs.
        """

        r = config.es.count(cls.es_index, cls.es_doc_type)
        return r['count']


    @classmethod
    def es_reset(cls):

        """
        Clear and recreate the index.
        """

        cls.es_delete()
        cls.es_create()
