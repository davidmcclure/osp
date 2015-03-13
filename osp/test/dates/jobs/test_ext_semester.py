

import pytest

from osp.corpus.models.document import Document
from osp.corpus.jobs.ext_text import ext_text
from osp.dates.models.semester import Document_Date_Semester
from osp.dates.jobs.ext_semester import ext_semester


@pytest.fixture()
def ext(models, mock_corpus):

    """
    Returns:
        function: A helper that creates document / text rows, runs the job,
        and returns the new `document_date_semester` row.
    """

    def _ext(content):

        # Create a document.
        path = mock_corpus.add_file(content=content)
        document = Document.create(path=path)

        # Extract text, then date.
        ext_text(document.id)
        ext_semester(document.id)

        # Pop out the new row.
        return (
            Document_Date_Semester
            .select()
            .where(Document_Date_Semester.document==document)
            .first()
        )

    return _ext


def test_fall_semester(ext):

    """
    Fall 2012
    """

    row = ext('abc Fall 2012 def')

    assert row.offset == 4
    assert row.date.year == 2012
    assert row.date.month == 9


def test_spring_semester(ext):

    """
    Spring 2012
    """

    row = ext('abc Spring 2012 def')

    assert row.offset == 4
    assert row.date.year == 2012
    assert row.date.month == 1


def test_ignore_case(ext):

    """
    The case of the semester should be ignored.
    """

    cases = [
        'abc FALL 2012 def',
        'abc fall 2012 def',
        'abc FaLl 2012 def'
    ]

    for case in cases:

        row = ext(case)

        assert row.offset == 4
        assert row.date.year == 2012
        assert row.date.month == 9


def test_two_digit_year(ext):

    """
    Fall 12
    """

    row = ext('abc Fall 12 def')

    assert row.offset == 4
    assert row.date.year == 2012
    assert row.date.month == 9


def test_apostrophe_before_year(ext):

    """
    Fall '12
    """

    row = ext("abc Fall '12 def")

    assert row.offset == 4
    assert row.date.year == 2012
    assert row.date.month == 9


def test_ignore_future_years(ext):

    """
    Fall 3000
    """

    row = ext("abc Fall 3000 def")
    assert row == None


def test_ignore_old_years(ext):

    """
    Fall 1979
    """

    row = ext("abc Fall 1979 def")
    assert row == None
