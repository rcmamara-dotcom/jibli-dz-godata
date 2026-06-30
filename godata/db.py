import os
from peewee import PostgresqlDatabase

database = PostgresqlDatabase(
    os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", 5432)),
    autorollback=True,
)


def init_db() -> None:
    """Crée les tables si elles n'existent pas (idempotent)."""
    from .models import User, Trip, Parcel
    with database:
        database.create_tables([User, Trip, Parcel], safe=True)
