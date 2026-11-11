import os
from peewee import PostgresqlDatabase

database = PostgresqlDatabase(None)


def init_db() -> None:
    """Configure la connexion, migre les nouvelles colonnes, puis crée les tables."""
    ssl = {"sslmode": "require"} if os.environ.get("DB_SSL", "true").lower() != "false" else {}
    database.init(
        os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        **ssl,
    )
    from .models import (
        User, Trip, Parcel, Review, Subscription, Shipment, ShipmentEvent, Conversation, Message, UserReview,
    )
    with database:
        # Run column migrations BEFORE create_tables so peewee
        # doesn't try to index columns that don't exist yet.
        _migrate_columns()
        first_user_reviews = not database.table_exists("user_reviews")
        database.create_tables(
            [User, Trip, Parcel, Review, Subscription, Shipment, ShipmentEvent, Conversation, Message, UserReview],
            safe=True,
        )
        _migrate_indexes()
        if first_user_reviews:
            _import_trip_reviews()


def _migrate_columns() -> None:
    """Add new columns to existing tables (safe to run multiple times).

    IF EXISTS : sur une base vide, un ALTER en échec annulerait la transaction
    et ferait échouer create_tables.
    """
    for sql in [
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS name VARCHAR(100)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS birth_date DATE",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS google_id VARCHAR(128)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'",
        "ALTER TABLE IF EXISTS users ADD COLUMN IF NOT EXISTS notify_messages BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE IF EXISTS parcels ADD COLUMN IF NOT EXISTS weight REAL",
        "ALTER TABLE IF EXISTS parcels ADD COLUMN IF NOT EXISTS length REAL",
        "ALTER TABLE IF EXISTS parcels ADD COLUMN IF NOT EXISTS width REAL",
        "ALTER TABLE IF EXISTS parcels ADD COLUMN IF NOT EXISTS height REAL",
        "ALTER TABLE IF EXISTS parcels ADD COLUMN IF NOT EXISTS parcel_type VARCHAR(20)",
    ]:
        try:
            database.execute_sql(sql)
        except Exception:
            pass


def _import_trip_reviews() -> None:
    """Une seule fois : les anciens avis de trajet deviennent des avis sur le voyageur (le plus récent par paire)."""
    try:
        with database.atomic():
            database.execute_sql(
                "INSERT INTO user_reviews (reviewer_id, reviewed_id, rating, comment, created_at, updated_at) "
                "SELECT DISTINCT ON (r.reviewer_id, t.owner_id) r.reviewer_id, t.owner_id, r.rating, r.comment, "
                "r.created_at, r.created_at "
                "FROM reviews r JOIN trips t ON t.id = r.trip_id "
                "WHERE t.owner_id IS NOT NULL AND t.owner_id <> r.reviewer_id "
                "ORDER BY r.reviewer_id, t.owner_id, r.created_at DESC "
                "ON CONFLICT DO NOTHING"
            )
    except Exception:
        pass


def _migrate_indexes() -> None:
    """Create indexes that need columns to exist first."""
    try:
        # Comptes Google antérieurs à la vérification e-mail : adresse déjà vérifiée par Google
        database.execute_sql(
            "UPDATE users SET email_verified = TRUE WHERE google_id IS NOT NULL AND email_verified = FALSE"
        )
        # les admins d'avant les rôles gardent leurs droits
        database.execute_sql("UPDATE users SET role = 'admin' WHERE is_admin = TRUE AND role = 'user'")
    except Exception:
        pass
    try:
        database.execute_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS users_google_id_key "
            "ON users (google_id) WHERE google_id IS NOT NULL"
        )
    except Exception:
        pass
