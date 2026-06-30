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
