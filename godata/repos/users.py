from datetime import date as DateType
from peewee import DoesNotExist
from ..models import User


class UserRepo:
    @staticmethod
    def create(
        email: str,
        password_hash: str,
        name: str | None = None,
        birth_date: DateType | None = None,
    ) -> User:
        return User.create(
            email=email,
            password_hash=password_hash,
            name=name,
            birth_date=birth_date,
        )

    @staticmethod
    def get_by_email(email: str) -> User | None:
        try:
            return User.get(User.email == email)
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        try:
            return User.get_by_id(user_id)
        except DoesNotExist:
            return None

    @staticmethod
    def get_by_google_id(google_id: str) -> User | None:
        try:
            return User.get(User.google_id == google_id)
        except DoesNotExist:
            return None

    @staticmethod
    def get_or_create_by_google(
        google_id: str, email: str, name: str | None = None
    ) -> User:
        """Find or create a user from a verified Google sign-in."""
        user = UserRepo.get_by_google_id(google_id)
        if user:
            return user
        user = UserRepo.get_by_email(email)
        if user:
            # Link existing email account to Google
            User.update(google_id=google_id, name=name or user.name).where(
                User.id == user.id
            ).execute()
            return UserRepo.get_by_id(user.id)  # type: ignore[return-value]
        return User.create(email=email, password_hash="", google_id=google_id, name=name)

    @staticmethod
    def list_all() -> list[User]:
        return list(User.select().order_by(User.created_at.desc()))

    @staticmethod
    def update_password(user_id: int, password_hash: str) -> bool:
        updated = User.update(password_hash=password_hash).where(User.id == user_id).execute()
        return updated > 0

    @staticmethod
    def force_delete(user_id: int) -> bool:
        deleted = User.delete().where(User.id == user_id).execute()
        return deleted > 0
