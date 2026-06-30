# godata

Data access layer for **Jibli DZ** — Peewee ORM models and repositories over PostgreSQL.

## Structure

```
godata/
├── db.py        # Database connection & init_db()
├── models.py    # Peewee models: User, Trip, Parcel
└── repos/
    ├── users.py
    ├── trips.py
    └── parcels.py
```

## Installation

```bash
pip install git+https://github.com/rcmamara-dotcom/jibli-dz-godata.git
```

## Environment variables

| Variable      | Default     | Description           |
|---------------|-------------|-----------------------|
| `DB_NAME`     | —           | PostgreSQL database   |
| `DB_USER`     | —           | PostgreSQL user       |
| `DB_PASSWORD` | —           | PostgreSQL password   |
| `DB_HOST`     | `localhost` | PostgreSQL host       |
| `DB_PORT`     | `5432`      | PostgreSQL port       |
