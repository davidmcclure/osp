

from osp.common.config import config
from osp.corpus.models import Document
from osp.corpus.models import Document_Index


def test_es_insert(add_doc):

    """
    Document_Index.es_insert() should index the document body and id.
    """

    doc = add_doc(content='text')

    Document_Index.es_insert()

    es_doc = config.es.get(
        index='osp',
        doc_type='document',
        id=doc.id,
    )

    assert es_doc['_id'] == str(doc.id)
    assert es_doc['_source']['body'] == 'text'