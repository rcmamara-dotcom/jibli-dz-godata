from datetime import datetime, timezone
from peewee import DoesNotExist
from ..models import Shipment, ShipmentEvent, Trip


class ShipmentRepo:
    @staticmethod
    def create(trip: Trip, sender_id: int, description: str) -> Shipment:
        shipment = Shipment.create(
            trip=trip,
            sender=sender_id,
            carrier=trip.owner_id,
            from_city=trip.from_city,
            to_city=trip.to_city,
            trip_date=trip.date,
            description=description,
        )
        ShipmentEvent.create(shipment=shipment, status=shipment.status)
        return shipment

    @staticmethod
    def get_by_id(shipment_id: int) -> Shipment | None:
        try:
            return Shipment.get_by_id(shipment_id)
        except DoesNotExist:
            return None

    @staticmethod
    def list_for_user(user_id: int) -> list[Shipment]:
        """Envois où l'utilisateur est expéditeur ou voyageur, plus récents d'abord."""
        return list(
            Shipment.select()
            .where((Shipment.sender == user_id) | (Shipment.carrier == user_id))
            .order_by(Shipment.created_at.desc())
        )

    @staticmethod
    def set_status(shipment: Shipment, status: str) -> Shipment:
        now = datetime.now(timezone.utc)
        Shipment.update(status=status, updated_at=now).where(Shipment.id == shipment.id).execute()
        ShipmentEvent.create(shipment=shipment, status=status, created_at=now)
        return Shipment.get_by_id(shipment.id)

    @staticmethod
    def events(shipment_id: int) -> list[ShipmentEvent]:
        return list(
            ShipmentEvent.select()
            .where(ShipmentEvent.shipment == shipment_id)
            .order_by(ShipmentEvent.created_at, ShipmentEvent.id)
        )
