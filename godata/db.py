import os
from peewee import PostgresqlDatabase

database = PostgresqlDatabase(None)


def init_db() -> None:
    """Configure la connexion et crée les tables (idempotent)."""
    ssl = {"sslmode": "require"} if os.environ.get("DB_SSL", "true").lower() != "false" else {}
    database.init(
        os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        autorollback=True,
        **ssl,
    )
    from .models import User, Trip, Parcel
    with database:
        database.create_tables([User, Trip, Parcel], safe=True)
