from peewee import DoesNotExist, JOIN
from ..models import Parcel, User


class ParcelRepo:
    @staticmethod
    def list_all() -> list[Parcel]:
        return list(
            Parcel.select(Parcel, User)
            .join(User, join_type=JOIN.LEFT_OUTER, on=(Parcel.owner == User.id))
            .order_by(Parcel.created_at.desc())
        )

    @staticmethod
    def get_by_id(parcel_id: int) -> Parcel | None:
        try:
            return Parcel.get_by_id(parcel_id)
        except DoesNotExist:
            return None

    @staticmethod
    def create(owner_id: int | None, **data: object) -> Parcel:
        return Parcel.create(owner_id=owner_id, **data)

    @staticmethod
    def delete(parcel_id: int, owner_id: int) -> bool:
        deleted = (
            Parcel.delete()
            .where(Parcel.id == parcel_id, Parcel.owner_id == owner_id)
            .execute()
        )
        return deleted > 0
