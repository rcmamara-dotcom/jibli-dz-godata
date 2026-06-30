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
