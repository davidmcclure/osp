

from osp.corpus.models.document import Document
from osp.citations.hlom.models.citation import HLOM_Citation
from osp.citations.hlom.models.record import HLOM_Record
from peewee import *


def text_counts():

    """
    Get an ordered list of MARC control number -> citation counts.
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
    Get an ordered list of document paths -> citation counts.
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


def records_with_citations():

    """
    Get all HLOM records that have at least one citation.
    """

    return (
        HLOM_Record
        .select()
        .where(HLOM_Record.metadata.exists('citation_count'))
    )


def deduped_records():

    """
    Get records with distinct deduping hashes.
    """

    return (
        records_with_citations()
        .distinct([HLOM_Record.metadata['deduping_hash']])
        .order_by(
            HLOM_Record.metadata['deduping_hash'],
            HLOM_Record.id
        )
    )


def document_objects():

    """
    Get document -> HLOM record IDs for Overview document-objects.
    """

    rid = HLOM_Record.stored_id.alias('rid')
    did = Document.stored_id.alias('did')

    return (
        HLOM_Citation
        .select(rid, did)
        .join(
            HLOM_Record,
            on=(HLOM_Citation.record==HLOM_Record.control_number)
        )
        .join(
            Document,
            on=(HLOM_Citation.document==Document.path)
        )
        .where(~(Document.stored_id >> None))
    )