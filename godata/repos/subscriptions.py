from datetime import datetime, timezone
from peewee import DoesNotExist
from ..models import Subscription


class SubscriptionRepo:
    @staticmethod
    def get_by_user(user_id: int) -> Subscription | None:
        try:
            return Subscription.get(Subscription.user == user_id)
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_stripe_id(stripe_subscription_id: str) -> Subscription | None:
        try:
            return Subscription.get(Subscription.stripe_subscription_id == stripe_subscription_id)
        except DoesNotExist:
            return None

    @staticmethod
    def upsert(
        user_id: int,
        plan: str,
        status: str,
        stripe_subscription_id: str,
        stripe_customer_id: str,
        current_period_start: datetime,
        current_period_end: datetime,
    ) -> Subscription:
        existing = SubscriptionRepo.get_by_user(user_id)
        if existing:
            Subscription.update(
                plan=plan,
                status=status,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
            ).where(Subscription.user == user_id).execute()
            return SubscriptionRepo.get_by_user(user_id)  # type: ignore[return-value]
        return Subscription.create(
            user=user_id,
            plan=plan,
            status=status,
            stripe_subscription_id=stripe_subscription_id,
            stripe_customer_id=stripe_customer_id,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
        )

    @staticmethod
    def update_status(stripe_subscription_id: str, status: str) -> None:
        Subscription.update(status=status).where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).execute()

    @staticmethod
    def delete_by_stripe_id(stripe_subscription_id: str) -> None:
        Subscription.delete().where(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).execute()
