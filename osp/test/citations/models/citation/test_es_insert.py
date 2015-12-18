

from osp.common.config import config
from osp.institutions.models import Institution_Document
from osp.citations.models import Citation


def test_citation_fields(elasticsearch, add_citation):

    """
    Local rows - text_id, document_id, and min_freq - should be included in
    the Elasticsearch document.
    """

    citation = add_citation()

    Citation.es_insert()

    doc = config.es.get(
        index='osp',
        doc_type='citation',
        id=citation.id,
    )

    assert doc['_source']['text_id'] == citation.text_id
    assert doc['_source']['document_id'] == citation.document_id
    assert doc['_source']['corpus'] == citation.text.corpus
    assert doc['_source']['min_freq'] == citation.min_freq


def test_field_refs(
    elasticsearch,
    add_citation,
    add_subfield,
    add_subfield_document,
):

    """
    When the document is linked with a subfield, subfield / field referenecs
    should be included in the document.
    """

    citation = add_citation()
    subfield = add_subfield()

    # Link subfield -> citation.
    add_subfield_document(subfield=subfield, document=citation.document)

    Citation.es_insert()

    doc = config.es.get(
        index='osp',
        doc_type='citation',
        id=citation.id,
    )

    assert doc['_source']['subfield_id'] == subfield.id
    assert doc['_source']['field_id'] == subfield.field_id


def test_institution_refs(elasticsearch, add_citation, add_institution):

    """
    When the document is linked with an institution, an institution reference
    should be included in the document.
    """

    citation = add_citation()

    institution = add_institution()

    # Link inst -> citation.
    Institution_Document.create(
        institution=institution,
        document=citation.document,
    )

    Citation.es_insert()

    doc = config.es.get(
        index='osp',
        doc_type='citation',
        id=citation.id,
    )

    assert doc['_source']['institution_id'] == institution.id