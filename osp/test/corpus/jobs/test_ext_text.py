

from osp.corpus.models.document import Document
from osp.corpus.models.text import Document_Text
from osp.corpus.jobs.ext_text import ext_text


def test_text_extraction_succeeds(models, mock_osp):

    """
    read_text() should extract text for a document and write the result into
    the `document_text` table.
    """

    # Add a file, create a document row.
    path = mock_osp.add_file(content='text')
    document = Document.create(path=path)

    ext_text(document.id)

    # Pop out the new row.
    row = Document_Text.get(Document_Text.document==document)
    assert row.text == 'text'


def test_text_extraction_fails(models, mock_osp):

    """
    If no text can be extracted, don't write the row.
    """

    # Add an empty file.
    path = mock_osp.add_file(content='')
    document = Document.create(path=path)

    ext_text(document.id)

    # Shouldn't write a row.
    assert Document_Text.select().count() == 0
