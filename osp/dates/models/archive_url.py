

import time

from osp.common.config import config
from osp.common.models.base import BaseModel
from osp.corpus.models.document import Document
from peewee import *


class Document_Date_Archive_Url(BaseModel):


    class Meta:
        database = config.get_table_db('document_date_archive_url')


    document = ForeignKeyField(Document, unique=True)
    date = DateTimeField()
