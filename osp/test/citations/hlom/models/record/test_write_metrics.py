

import numpy as np

from osp.citations.hlom.models.record import HLOM_Record
from osp.citations.hlom.models.citation import HLOM_Citation
from .utils import score


def test_write_metrics(models, add_hlom, add_doc):

    """
    HLOM_Record.write_metrics() should write 1,2,3... rankings and a
    "percentile" scored, based on the log-ratio of the rank.
    """

    r1 = add_hlom('title1', 'author1')
    r2 = add_hlom('title2', 'author2')
    r3 = add_hlom('title3', 'author3')

    # 1 citation for r1.
    d1 = add_doc('content1')
    HLOM_Citation.create(record=r1, document=d1)

    # 2 citations for r2.
    d2 = add_doc('content2')
    d3 = add_doc('content3')
    HLOM_Citation.create(record=r2, document=d2)
    HLOM_Citation.create(record=r2, document=d3)

    # 3 citations for r3.
    d4 = add_doc('content4')
    d5 = add_doc('content5')
    d6 = add_doc('content6')
    HLOM_Citation.create(record=r3, document=d4)
    HLOM_Citation.create(record=r3, document=d5)
    HLOM_Citation.create(record=r3, document=d6)

    HLOM_Record.write_stats()
    HLOM_Record.write_metrics()

    r1 = HLOM_Record.reload(r1)
    r2 = HLOM_Record.reload(r2)
    r3 = HLOM_Record.reload(r3)

    assert r3.metadata['rank'] == 1
    assert r2.metadata['rank'] == 2
    assert r1.metadata['rank'] == 3

    assert r3.metadata['score'] == score(3, 3)
    assert r2.metadata['score'] == score(2, 3)
    assert r1.metadata['score'] == score(1, 3)
