import datetime

from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *

import config

DATABASE = SqliteDatabase('todos.sqlite')
HASHER = PasswordHasher()


class Todo(Model):
    name = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    #Created_by = ForeignKeyField(User, related_name='todo_set')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Todo], safe=True)
    DATABASE.close()
