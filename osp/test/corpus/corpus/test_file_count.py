

from osp.corpus.corpus import Corpus
from osp.test.utils import segment_range


def test_file_count(mock_osp):

    """
    Corpus#file_count should return the number of files in all segments.
    """

    # 10 segments, each with 10 files.
    for s in segment_range(10):
        for i in range(10):
            mock_osp.add_file(segment=s, name=str(i))

    corpus = Corpus(mock_osp.path)
    assert corpus.file_count == 100
