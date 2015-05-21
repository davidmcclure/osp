

from osp.citations.hlom.models.citation import HLOM_Citation
from osp.institutions.models.institution import Institution
from osp.locations.models.doc_inst import Document_Institution


def test_index_states(add_hlom, add_doc):

    """
    HLOM_Citation.index_state() should denormalize state abbrevations from the
    institution associated with the citation.
    """

    t1 = add_hlom()
    t2 = add_hlom()
    t3 = add_hlom()

    s1 = add_doc('syllabus1')
    s2 = add_doc('syllabus2')
    s3 = add_doc('syllabus3')

    c1 = HLOM_Citation.create(document=s1, record=t1)
    c2 = HLOM_Citation.create(document=s2, record=t2)
    c3 = HLOM_Citation.create(document=s3, record=t3)

    i1 = Institution.create()
    i2 = Institution.create()
    i3 = Institution.create()

    # Link documents -> institutions.
    Document_Institution.create(document=t1, institution=i1)
    Document_Institution.create(document=t2, institution=i2)
    Document_Institution.create(document=t3, institution=i3)

    HLOM_Citation.index_institutions()

    c1 = HLOM_Citation.reload(c1)
    c2 = HLOM_Citation.reload(c2)
    c3 = HLOM_Citation.reload(c3)

    assert c1.institution == i1
    assert c2.institution == i2
    assert c3.institution == i3