

import datetime

from osp.common.config import config
from osp.corpus.models.document import Document
from peewee import *


class Document_Stored_Id(Model):


    created = DateTimeField(default=datetime.datetime.now)
    document = ForeignKeyField(Document, unique=True)
    stored_id = BigIntegerField(null=True)


    class Meta:
        database = config.get_db('document_stored_id')
