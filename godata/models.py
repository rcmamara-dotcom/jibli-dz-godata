from datetime import datetime, timezone
from peewee import (
    Model, AutoField, BooleanField, CharField, TextField,
    FloatField, IntegerField, DateField, DateTimeField, ForeignKeyField,
)
from .db import database


class BaseModel(Model):
    class Meta:
        database = database


# Rôles du moins au plus élevé ; les droits de chacun sont définis dans l'API.
ROLES = ("user", "vip", "moderator", "admin")


class User(BaseModel):
    id = AutoField()
    email = CharField(max_length=255, unique=True)
    password_hash = CharField(max_length=255)
    name = CharField(max_length=100, null=True)
    birth_date = DateField(null=True)
    phone = CharField(max_length=20, null=True)  # null pour les comptes créés avant l'ajout
    email_verified = BooleanField(default=False)
    # unique enforced via partial index in migration (null-safe)
    google_id = CharField(max_length=128, null=True)
    is_admin = BooleanField(default=False)  # = role == "admin", gardé pour compatibilité
    role = CharField(max_length=20, default="user")  # voir ROLES
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


PARCEL_TYPES = ("vetements", "alimentaire", "electronique", "medicaments", "documents", "autre")


class Parcel(BaseModel):
    id = AutoField()
    owner = ForeignKeyField(User, backref="parcels", null=True, on_delete="SET NULL")
    from_city = CharField(max_length=100)
    to_city = CharField(max_length=100)
    description = TextField()
    budget = FloatField(default=0)
    wa = CharField(max_length=20)
    weight = FloatField(null=True)       # kg
    length = FloatField(null=True)       # cm
    width = FloatField(null=True)        # cm
    height = FloatField(null=True)       # cm
    parcel_type = CharField(max_length=20, null=True)  # voir PARCEL_TYPES
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "parcels"


class Subscription(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref="subscriptions", on_delete="CASCADE", unique=True)
    plan = CharField(max_length=20)  # starter | voyageur | pro
    status = CharField(max_length=20)  # active | cancelled | past_due | incomplete
    stripe_subscription_id = CharField(max_length=128, unique=True)
    stripe_customer_id = CharField(max_length=128)
    current_period_start = DateTimeField()
    current_period_end = DateTimeField()
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "subscriptions"


class Review(BaseModel):
    id = AutoField()
    trip = ForeignKeyField(Trip, backref="reviews", on_delete="CASCADE")
    reviewer = ForeignKeyField(User, backref="given_reviews", on_delete="CASCADE")
    rating = IntegerField()          # 1 à 5
    comment = TextField(null=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "reviews"
        indexes = ((("trip", "reviewer"), True),)   # un seul avis par (trajet, user)


# Étapes d'un envoi, dans l'ordre. "cancelled" est hors parcours.
SHIPMENT_STEPS = ("deposited", "accepted", "picked_up", "in_transit", "arrived", "delivered")
SHIPMENT_CANCELLED = "cancelled"


class Shipment(BaseModel):
    """Un colis confié à un voyageur, suivi étape par étape."""
    id = AutoField()
    # SET NULL : le trajet est supprimé après sa date, le suivi doit rester
    trip = ForeignKeyField(Trip, backref="shipments", null=True, on_delete="SET NULL")
    sender = ForeignKeyField(User, backref="sent_shipments", on_delete="CASCADE")
    carrier = ForeignKeyField(User, backref="carried_shipments", on_delete="CASCADE")
    # copiés du trajet pour la même raison
    from_city = CharField(max_length=100)
    to_city = CharField(max_length=100)
    trip_date = DateField(null=True)
    description = TextField()
    status = CharField(max_length=20, default="deposited")
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "shipments"


class ShipmentEvent(BaseModel):
    """Historique : une ligne par changement d'étape (date affichée sous chaque point)."""
    id = AutoField()
    shipment = ForeignKeyField(Shipment, backref="events", on_delete="CASCADE")
    status = CharField(max_length=20)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "shipment_events"


class Conversation(BaseModel):
    """Fil de messagerie privée entre deux utilisateurs, lié à une annonce."""
    id = AutoField()
    initiator = ForeignKeyField(User, backref="initiated_conversations", on_delete="CASCADE")
    recipient = ForeignKeyField(User, backref="received_conversations", on_delete="CASCADE")
    # Lié à un trajet OU un colis (au plus un des deux)
    trip = ForeignKeyField(Trip, backref="conversations", null=True, on_delete="SET NULL")
    parcel = ForeignKeyField(Parcel, backref="conversations", null=True, on_delete="SET NULL")
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "conversations"


class Message(BaseModel):
    """Un message dans une conversation."""
    id = AutoField()
    conversation = ForeignKeyField(Conversation, backref="messages", on_delete="CASCADE")
    sender = ForeignKeyField(User, backref="sent_messages", on_delete="CASCADE")
    content = TextField()
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "messages"
