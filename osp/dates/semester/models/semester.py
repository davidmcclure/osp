

import datetime

from osp.common.models.base import BaseModel
from peewee import *


class Document_Semester(BaseModel):

    created = DateTimeField(default=datetime.datetime.now)
    document = CharField()
    year = IntegerField()
    semester = CharField()
