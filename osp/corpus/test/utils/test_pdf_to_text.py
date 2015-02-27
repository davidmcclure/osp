

import pytest

from osp.corpus.test.mocks.corpus import MockCorpus
from osp.corpus.utils import pdf_to_text


def test_extract_text():

    """
    Text in pages should be extracted and concatenated.
    """

    corpus = MockCorpus()

    # Create a PDF with 3 pages.
    path = corpus.add_file('000', 'text', 'pdf')

    # Should extract the text.
    text = pdf_to_text(path).strip()
    assert text == 'text'
