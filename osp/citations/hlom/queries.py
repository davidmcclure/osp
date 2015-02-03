

from peewee import *
from osp.citations.hlom.models.citation import HLOM_Citation


def text_counts():

    """
    Map texts to citation counts.
    """

    count = fn.Count(HLOM_Citation.id)

    return (
        HLOM_Citation
        .select(
            HLOM_Citation.record,
            count.alias('count')
        )
        .group_by(HLOM_Citation.record)
        .distinct(HLOM_Citation.record)
        .order_by(count.desc())
    )


def syllabus_counts():

    """
    Map syllabi to citation counts.
    """

    count = fn.Count(HLOM_Citation.id)

    return (
        HLOM_Citation
        .select(
            HLOM_Citation.document,
            count.alias('count')
        )
        .group_by(HLOM_Citation.document)
        .distinct(HLOM_Citation.document)
        .order_by(count.desc())
    )
