from peewee import DoesNotExist
from ..models import User


class UserRepo:
    @staticmethod
    def create(email: str, password_hash: str) -> User:
        return User.create(email=email, password_hash=password_hash)

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
