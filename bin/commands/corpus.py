

import os
import click
import csv
import random
import sys

from osp.common.config import config
from osp.common.utils import query_bar
from osp.corpus.corpus import Corpus
from osp.corpus.models.document import Document
from osp.corpus.models.format import Document_Format
from osp.corpus.models.text import Document_Text
from osp.corpus.models.tsvector import Document_TSVector
from osp.corpus.jobs.ext_format import ext_format
from osp.corpus.jobs.ext_text import ext_text
from peewee import create_model_tables
from prettytable import PrettyTable


@click.group()
def cli():
    pass


@cli.command()
def init_db():

    """
    Create the database tables.
    """

    create_model_tables([
        Document,
        Document_Format,
        Document_TSVector,
        Document_Text
    ], fail_silently=True)


@cli.command()
def insert_documents():

    """
    Insert documents in the database.
    """

    Document.insert_documents()


@cli.command()
def queue_format():

    """
    Queue format extraction tasks in the worker.
    """

    for doc in query_bar(Document.select()):
        config.rq.enqueue(ext_format, doc.id)


@cli.command()
def queue_text():

    """
    Queue text extraction tasks in the worker.
    """

    for doc in query_bar(Document.select()):
        config.rq.enqueue(ext_text, doc.id)


@cli.command()
def format_counts():

    """
    Print a table of file format -> count.
    """

    t = PrettyTable(['File Type', 'Doc Count'])
    t.align = 'l'

    for c in Document_Format.format_counts():
        t.add_row(c)

    click.echo(t)


@cli.command()
def file_count():

    """
    Print the total number of files.
    """

    corpus = Corpus.from_env()
    click.echo(corpus.file_count)
