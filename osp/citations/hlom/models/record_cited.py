

from osp.common.config import config
from osp.citations.hlom.models.citation import HLOM_Citation
from osp.citations.hlom.models.record import HLOM_Record
from peewee import fn


class HLOM_Record_Cited(HLOM_Record):


    class Meta:
        database = config.get_table_db('hlom_record_cited')


    @classmethod
    def copy_records(cls):

        """
        Copy in cited records.
        """

        cited = (

            HLOM_Record
            .select()

            # Coalesce duplicates.
            .distinct([HLOM_Record.metadata['deduping_hash']])
            .order_by(
                HLOM_Record.metadata['deduping_hash'],
                HLOM_Record.id
            )

            .group_by(HLOM_Record.id)
            .join(HLOM_Citation)

        )

        for c in cited:
            cls.create(**c._data)


    @classmethod
    def rank(cls):

        """
        Initialize a ranking query.

        Returns:
            peewee.SelectQuery
        """

        count = fn.Count(HLOM_Citation.id)

        return (

            cls.select(cls, count)

            # Join citations.
            .join(HLOM_Citation, on=(
                cls.id==HLOM_Citation.record
            ))

            .group_by(cls.id)
            .order_by(count.desc())
            .naive()

        )
