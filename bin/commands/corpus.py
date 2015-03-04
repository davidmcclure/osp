

import os
import click
import csv
import sys

from osp.common.config import config
from osp.common.models.base import redis
from osp.common.utils import query_bar
from osp.corpus.corpus import Corpus
from osp.corpus.models.document import Document
from osp.corpus.models.stored_id import Document_Stored_Id
from osp.corpus.models.format import Document_Format
from osp.corpus.models.text import Document_Text
from osp.corpus.jobs.read_format import read_format
from osp.corpus.jobs.read_text import read_text
from osp.corpus import queries
from peewee import create_model_tables
from collections import Counter
from clint.textui.progress import bar
from prettytable import PrettyTable
from rq import Queue


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
        Document_Stored_Id,
        Document_Text,
        Document_Format
    ], fail_silently=True)


@cli.command()
def insert_documents():

    """
    Insert documents in the database.
    """

    corpus = Corpus.from_env()
    Document.insert_documents(corpus)


@cli.command()
def queue_read_format():

    """
    Queue format extraction tasks in the worker.
    """

    queue = Queue(connection=redis)

    for doc in query_bar(Document.select()):
        queue.enqueue(read_format, doc.id)


@cli.command()
def queue_read_text():

    """
    Queue text extraction tasks in the worker.
    """

    queue = Queue(connection=redis)

    for doc in query_bar(Document.select()):
        queue.enqueue(read_text, doc.id)


@cli.command()
def format_counts():

    """
    Print a table of file format -> count.
    """

    t = PrettyTable(['File Type', 'Doc Count'])
    t.align = 'l'

    for c in queries.format_counts().naive().iterator():
        t.add_row([c.format, c.count])

    click.echo(t)


@cli.command()
def file_count():

    """
    Print the total number of files.
    """

    corpus = Corpus.from_env()
    click.echo(corpus.file_count)


@cli.command()
@click.argument('out_path', type=click.Path())
@click.option('--frag_len', default=1500)
@click.option('--page_len', default=10000)
def truncated_csv(out_path, frag_len, page_len):

    """
    Write a CSV with truncated document texts.
    """

    out_file = open(out_path, 'w')

    # CSV writer.
    cols = ['id', 'title', 'text']
    writer = csv.DictWriter(out_file, cols)
    writer.writeheader()

    for row in query_bar(Document_Text.select()):

        # Truncate the text.
        fragment = row.text[:frag_len]

        writer.writerow({
            'id': row.document,
            'title': row.document,
            'text': fragment
        })
