

import click

from osp.common.utils import query_bar
from osp.corpus.models.document import Document
from osp.dates.models.archive_url import Document_Date_Archive_Url
from osp.dates.models.semester import Document_Date_Semester
from osp.dates.models.file_metadata import Document_Date_File_Metadata
from osp.dates.jobs.ext_archive_url import ext_archive_url
from osp.dates.jobs.ext_semester import ext_semester
from peewee import create_model_tables
from osp.common.models.base import queue


@click.group()
def cli():
    pass


@cli.command()
def init_db():

    """
    Create the database tables.
    """

    create_model_tables([
        Document_Date_Archive_Url,
        Document_Date_Semester,
        Document_Date_File_Metadata
    ], fail_silently=True)


@cli.command()
def queue_archive_url():

    """
    Queue Internet Archive timestamp extraction tasks.
    """

    for doc in query_bar(Document.select()):
        queue.enqueue(ext_archive_url, doc.id)


@cli.command()
def queue_semester():

    """
    Queue semester regex extraction tasks.
    """

    for doc in query_bar(Document.select()):
        queue.enqueue(ext_semester, doc.id)
