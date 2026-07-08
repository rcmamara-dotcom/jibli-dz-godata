import datetime
from peewee import DoesNotExist, JOIN
from ..models import Trip, User


class TripRepo:
    @staticmethod
    def list_all() -> list[Trip]:
        return list(
            Trip.select(Trip, User)
            .join(User, join_type=JOIN.LEFT_OUTER, on=(Trip.owner == User.id))
            .order_by(Trip.created_at.desc())
        )

    @staticmethod
    def get_by_id(trip_id: int) -> Trip | None:
        try:
            return Trip.get_by_id(trip_id)
        except DoesNotExist:
            return None

    @staticmethod
    def create(owner_id: int | None, **data: object) -> Trip:
        return Trip.create(owner_id=owner_id, **data)

    @staticmethod
    def delete(trip_id: int, owner_id: int) -> bool:
        deleted = (
            Trip.delete()
            .where(Trip.id == trip_id, Trip.owner_id == owner_id)
            .execute()
        )
        return deleted > 0

    @staticmethod
    def list_expiring_on(target_date: datetime.date) -> list[Trip]:
        """Return trips whose travel date equals target_date, with owner pre-fetched."""
        return list(
            Trip.select(Trip, User)
            .join(User, join_type=JOIN.LEFT_OUTER, on=(Trip.owner == User.id))
            .where(Trip.date == target_date)
        )

    @staticmethod
    def force_delete(trip_id: int) -> bool:
        return Trip.delete().where(Trip.id == trip_id).execute() > 0

    @staticmethod
    def pop_expired(before: datetime.date) -> list[Trip]:
        """Return then delete all trips with date strictly before `before`."""
        expired = list(
            Trip.select(Trip, User)
            .join(User, join_type=JOIN.LEFT_OUTER, on=(Trip.owner == User.id))
            .where(Trip.date < before)
        )
        if expired:
            Trip.delete().where(Trip.date < before).execute()
        return expired
