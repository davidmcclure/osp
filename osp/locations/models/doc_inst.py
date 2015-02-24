

import datetime

from osp.common.models.base import RemoteModel
from osp.institutions.models.institution import Institution
from peewee import *


class Document_Institution(RemoteModel):

    created = DateTimeField(default=datetime.datetime.now)
    document = CharField(index=True)
    institution = ForeignKeyField(Institution)
