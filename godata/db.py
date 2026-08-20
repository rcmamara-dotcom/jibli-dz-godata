import os
from peewee import PostgresqlDatabase

database = PostgresqlDatabase(None)


def init_db() -> None:
    """Configure la connexion, crée les tables et migre les nouvelles colonnes."""
    ssl = {"sslmode": "require"} if os.environ.get("DB_SSL", "true").lower() != "false" else {}
    database.init(
        os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        **ssl,
    )
    from .models import User, Trip, Parcel, Review
    with database:
        database.create_tables([User, Trip, Parcel, Review], safe=True)
        # Migrate new columns — safe to run multiple times
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(100)",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_date DATE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(128)",
        ]
        for sql in migrations:
            try:
                database.execute_sql(sql)
            except Exception:
                pass
        # Unique index for google_id (nullable)
        try:
            database.execute_sql(
                "CREATE UNIQUE INDEX IF NOT EXISTS users_google_id_key "
                "ON users (google_id) WHERE google_id IS NOT NULL"
            )
        except Exception:
            pass
