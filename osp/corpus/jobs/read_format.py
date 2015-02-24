

from osp.corpus.models.document import Document
from osp.corpus.models.format import Document_Format
from osp.corpus.syllabus import Syllabus


def read_format(id):

    """
    Write the libmagic file format.

    :param id: The document id.
    """

    doc = Document.select(Document.id==id)

    Document_Format.create(
        format=doc.syllabus.libmagic_file_type,
        document=syllabus.relative_path
    )
