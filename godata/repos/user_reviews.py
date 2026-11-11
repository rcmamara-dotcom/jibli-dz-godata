from datetime import datetime, timezone
from peewee import fn
from ..models import Conversation, Message, User, UserReview


class UserReviewRepo:

    @staticmethod
    def upsert(reviewer_id: int, reviewed_id: int, rating: int, comment: str | None) -> UserReview:
        """Crée l'avis, ou remplace celui que reviewer avait déjà laissé à reviewed."""
        now = datetime.now(timezone.utc)
        existing = UserReviewRepo.get(reviewer_id, reviewed_id)
        if existing:
            existing.rating, existing.comment, existing.updated_at = rating, comment or None, now
            existing.save()
            return existing
        return UserReview.create(reviewer=reviewer_id, reviewed=reviewed_id, rating=rating, comment=comment or None)

    @staticmethod
    def get(reviewer_id: int, reviewed_id: int) -> UserReview | None:
        return UserReview.get_or_none((UserReview.reviewer == reviewer_id) & (UserReview.reviewed == reviewed_id))

    @staticmethod
    def list_for(user_id: int, limit: int = 50) -> list[UserReview]:
        return list(
            UserReview.select(UserReview, User)
            .join(User, on=(UserReview.reviewer == User.id))
            .where(UserReview.reviewed == user_id)
            .order_by(UserReview.updated_at.desc())
            .limit(limit)
        )

    @staticmethod
    def summary(user_id: int) -> dict:
        """{avg, count, distribution: {5: n, 4: n, …}}."""
        rows = (
            UserReview.select(UserReview.rating, fn.COUNT(UserReview.id))
            .where(UserReview.reviewed == user_id)
            .group_by(UserReview.rating)
            .tuples()
        )
        dist = {i: 0 for i in range(1, 6)}
        for rating, n in rows:
            dist[int(rating)] = int(n)
        count = sum(dist.values())
        avg = round(sum(r * n for r, n in dist.items()) / count, 1) if count else None
        return {"avg": avg, "count": count, "distribution": dist}

    @staticmethod
    def bulk(user_ids: list[int]) -> dict[int, dict]:
        """{user_id: {avg, count}} en une seule requête."""
        if not user_ids:
            return {}
        rows = (
            UserReview.select(UserReview.reviewed, fn.ROUND(fn.AVG(UserReview.rating), 1), fn.COUNT(UserReview.id))
            .where(UserReview.reviewed.in_(user_ids))
            .group_by(UserReview.reviewed)
            .tuples()
        )
        return {int(uid): {"avg": float(avg), "count": int(n)} for uid, avg, n in rows}

    @staticmethod
    def can_review(reviewer_id: int, reviewed_id: int) -> bool:
        """Vrai si les deux ont vraiment échangé : chacun a écrit dans une conversation commune."""
        if reviewer_id == reviewed_id:
            return False
        shared = Conversation.select(Conversation.id).where(
            ((Conversation.initiator == reviewer_id) & (Conversation.recipient == reviewed_id))
            | ((Conversation.initiator == reviewed_id) & (Conversation.recipient == reviewer_id))
        )
        wrote = lambda uid: Message.select(Message.conversation).where(  # noqa: E731
            (Message.conversation.in_(shared)) & (Message.sender == uid)
        )
        return (
            Conversation.select()
            .where(Conversation.id.in_(wrote(reviewer_id)) & Conversation.id.in_(wrote(reviewed_id)))
            .exists()
        )

    @staticmethod
    def list_all() -> list[UserReview]:
        return list(UserReview.select().order_by(UserReview.updated_at.desc()))

    @staticmethod
    def force_delete(review_id: int) -> bool:
        return UserReview.delete().where(UserReview.id == review_id).execute() > 0
