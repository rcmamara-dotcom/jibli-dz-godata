from peewee import fn, DoesNotExist, JOIN, IntegrityError
from ..models import Review, Trip, User


class ReviewRepo:

    @staticmethod
    def list_for_trip(trip_id: int) -> list[Review]:
        return list(
            Review.select(Review, User)
            .join(User, on=(Review.reviewer == User.id))
            .where(Review.trip_id == trip_id)
            .order_by(Review.created_at.desc())
        )

    @staticmethod
    def rating_by_owner(owner_id: int) -> dict:
        """Moyenne et nombre d'avis sur tous les trajets de ce voyageur."""
        row = (
            Review
            .select(
                fn.ROUND(fn.AVG(Review.rating), 1).alias("avg"),
                fn.COUNT(Review.id).alias("count"),
            )
            .join(Trip, on=(Review.trip == Trip.id))
            .where(Trip.owner_id == owner_id)
            .tuples()
            .first()
        )
        avg, count = row if row else (None, 0)
        return {"avg": float(avg) if avg is not None else None, "count": int(count)}

    @staticmethod
    def bulk_ratings(owner_ids: list[int]) -> dict[int, dict]:
        """Retourne {owner_id: {avg, count}} en une seule requête."""
        if not owner_ids:
            return {}
        rows = (
            Review
            .select(
                Trip.owner_id,
                fn.ROUND(fn.AVG(Review.rating), 1).alias("avg"),
                fn.COUNT(Review.id).alias("count"),
            )
            .join(Trip, on=(Review.trip == Trip.id))
            .where(Trip.owner_id.in_(owner_ids))
            .group_by(Trip.owner_id)
            .tuples()
        )
        return {
            int(owner_id): {"avg": float(avg) if avg else None, "count": int(count)}
            for owner_id, avg, count in rows
        }

    @staticmethod
    def exists(trip_id: int, reviewer_id: int) -> bool:
        return Review.select().where(
            Review.trip_id == trip_id,
            Review.reviewer_id == reviewer_id,
        ).exists()

    @staticmethod
    def create(trip_id: int, reviewer_id: int, rating: int, comment: str | None) -> Review:
        return Review.create(
            trip_id=trip_id,
            reviewer_id=reviewer_id,
            rating=rating,
            comment=comment or None,
        )
