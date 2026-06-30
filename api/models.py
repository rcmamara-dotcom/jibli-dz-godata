from datetime import datetime, timezone
from peewee import (
    Model, AutoField, CharField, TextField,
    FloatField, DateField, DateTimeField, ForeignKeyField,
)
from .db import database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    id = AutoField()
    email = CharField(max_length=255, unique=True)
    password_hash = CharField(max_length=255)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "users"


class Trip(BaseModel):
    id = AutoField()
    owner = ForeignKeyField(User, backref="trips", null=True, on_delete="SET NULL")
    name = CharField(max_length=100)
    from_city = CharField(max_length=100)
    to_city = CharField(max_length=100)
    date = DateField()
    capacity = CharField(max_length=10)
    weight = FloatField(null=True)
    cap_desc = TextField(null=True)
    wa = CharField(max_length=20)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "trips"


class Parcel(BaseModel):
    id = AutoField()
    owner = ForeignKeyField(User, backref="parcels", null=True, on_delete="SET NULL")
    from_city = CharField(max_length=100)
    to_city = CharField(max_length=100)
    description = TextField()
    budget = FloatField(default=0)
    wa = CharField(max_length=20)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "parcels"
