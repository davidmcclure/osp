

from osp.corpus.utils import pdf_text


def test_extract_text(mock_osp):

    """
    Text in pages should be extracted and concatenated.
    """

    # Create a PDF with 3 pages.
    path = mock_osp.add_file(content='text', ftype='pdf')

    # Should extract the text.
    text = pdf_text(path).strip()
    assert text == 'text'
