

import click

from osp.common.models.base import postgres, redis
from osp.dates.semester.models.semester import Document_Semester
from osp.dates.semester.jobs.ext_semester import ext_semester
from rq import Queue


@click.group()
def cli():
    pass


@cli.command()
def init_db():

    """
    Create the database tables.
    """

    postgres.connect()

    postgres.create_tables([
        Document_Semester
    ], safe=True)


@cli.command()
def queue_semester_extraction():

    """
    Queue semester extraction queries.
    """

    pass
