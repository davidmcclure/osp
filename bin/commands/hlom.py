

import click
import sys
import numpy as np
import csv

from osp.common.models.base import queue
from osp.common.overview import Overview
from osp.common.utils import query_bar, grouper
from osp.citations.hlom.models.record import HLOM_Record
from osp.citations.hlom.models.citation import HLOM_Citation
from osp.citations.hlom.dataset import Dataset
from osp.citations.hlom.jobs.query import query
from osp.citations.hlom import queries
from osp.corpus.models.document import Document
from peewee import create_model_tables
from playhouse.postgres_ext import ServerSide
from clint.textui.progress import bar
from scipy.stats import rankdata
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
        HLOM_Record,
        HLOM_Citation,
    ], fail_silently=True)


@cli.command()
@click.option('--n', default=10000)
def insert_records(n):

    """
    Write the records into the database.
    """

    dataset = Dataset.from_env()

    i = 0
    for group in dataset.grouped_records(n):

        rows = []
        for record in group:

            # Just records with title/author.
            if record and record.title() and record.author():
                rows.append({
                    'control_number': record['001'].format_field(),
                    'record': record.as_marc()
                })

        if rows:
            HLOM_Record.insert_many(rows).execute()

        i += 1
        sys.stdout.write('\r'+str(i*n))
        sys.stdout.flush()


@cli.command()
def queue_queries():

    """
    Queue citation extraction queries.
    """

    for record in ServerSide(HLOM_Record.select()):
        queue.enqueue(query, record.id)


@cli.command()
@click.argument('out_path', type=click.Path())
def csv_text_counts(out_path):

    """
    Write a CSV with text -> assignment count.
    """

    out_file = open(out_path, 'w')

    # CSV writer.
    cols = ['title', 'author', 'count', 'subjects']
    writer = csv.DictWriter(out_file, cols)
    writer.writeheader()

    rows = []
    for c in queries.text_counts().naive().iterator():

        row = HLOM_Record.get(
            HLOM_Record.control_number==c.record
        )

        # Gather subject field values.
        subjects = [s.format_field() for s in row.pymarc.subjects()]

        rows.append({
            'title': row.pymarc.title(),
            'author': row.pymarc.author(),
            'count': c.count,
            'subjects': ','.join(subjects)
        })

    writer.writerows(rows)


@cli.command()
@click.argument('out_path', type=click.Path())
def csv_syllabus_counts(out_path):

    """
    Write a CSV with syllabus -> citation count.
    """

    out_file = open(out_path, 'w')

    # CSV writer.
    cols = ['document', 'count']
    writer = csv.DictWriter(out_file, cols)
    writer.writeheader()

    rows = []
    for c in queries.syllabus_counts().naive().iterator():

        rows.append({
            'document': c.document,
            'count': c.count
        })

    writer.writerows(rows)


@cli.command()
def write_citation_counts():

    """
    Cache a citation count value on the HLOM records.
    """

    query = query_bar(queries.text_counts())

    for pair in query:

        # Get a modified HSTORE value.
        updated = HLOM_Record.metadata.update(
            citation_count=str(pair.count)
        )

        # Update the HLOM record.
        query = (
            HLOM_Record
            .update(metadata=updated)
            .where(HLOM_Record.control_number==pair.record)
        )

        query.execute()


@cli.command()
def write_deduping_hash():

    """
    Cache a "deduping" hash on HLOM records.
    """

    query = query_bar(queries.records_with_citations())

    for record in query:

        # Get a modified HSTORE value.
        updated = HLOM_Record.metadata.update(
            deduping_hash=record.hash
        )

        # Update the HLOM record.
        query = (
            HLOM_Record
            .update(metadata=updated)
            .where(HLOM_Record.id==record.id)
        )

        query.execute()


@cli.command()
@click.argument('in_file', type=click.File('rt'))
def write_blacklist(in_file):

    """
    Flag blacklisted HLOM records.
    """

    for number in in_file.read().splitlines():

        # Get a modified HSTORE value.
        updated = HLOM_Record.metadata.update(
            blacklisted=''
        )

        # Update the HLOM record.
        query = (
            HLOM_Record
            .update(metadata=updated)
            .where(HLOM_Record.control_number==number)
        )

        query.execute()


@cli.command()
def write_metrics():

    """
    Write ranking scores for HLOM records.
    """

    # Get a set of id -> count tuples.
    pairs = []
    for record in queries.deduped_records():
        pairs.append((
            record.id,
            record.metadata['citation_count'])
        )

    # Get min/max ranks.
    counts = [p[1] for p in pairs]
    max_ranks = rankdata(counts, 'max')
    min_ranks = rankdata(counts, 'min')

    # Rank in ascending order.
    max_ranks = max_ranks.max()+1 - max_ranks
    min_ranks = min_ranks.max()+1 - min_ranks

    log_max = np.log(len(pairs))
    for i, pair in enumerate(bar(pairs)):

        max_rank = int(max_ranks[i])
        min_rank = int(min_ranks[i])

        # Log-percentage in the rank stack.
        percentile = ((log_max-np.log(min_rank))/log_max)*100

        # Get a modified HSTORE value.
        updated = HLOM_Record.metadata.update(
            teaching_rank=str(max_rank),
            teaching_percentile=str(percentile)
        )

        # Update the HLOM record.
        query = (
            HLOM_Record
            .update(metadata=updated)
            .where(HLOM_Record.id==pair[0])
        )

        query.execute()
