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
        phone: str | None = None,
    ) -> User:
        return User.create(
            email=email,
            password_hash=password_hash,
            name=name,
            birth_date=birth_date,
            phone=phone,
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
            if not user.email_verified:
                # compte Google créé avant la vérification e-mail : Google a déjà vérifié l'adresse
                UserRepo.set_email_verified(user.id)
                user.email_verified = True
            return user
        user = UserRepo.get_by_email(email)
        if user:
            # Link existing email account to Google
            User.update(google_id=google_id, name=name or user.name, email_verified=True).where(
                User.id == user.id
            ).execute()
            return UserRepo.get_by_id(user.id)  # type: ignore[return-value]
        return User.create(
            email=email, password_hash="", google_id=google_id, name=name, email_verified=True
        )

    @staticmethod
    def list_all() -> list[User]:
        return list(User.select().order_by(User.created_at.desc()))

    @staticmethod
    def update_password(user_id: int, password_hash: str) -> bool:
        updated = User.update(password_hash=password_hash).where(User.id == user_id).execute()
        return updated > 0

    @staticmethod
    def update_profile(user_id: int, **fields) -> bool:
        """Met à jour name / phone / birth_date (seuls les champs passés)."""
        allowed = {k: v for k, v in fields.items() if k in ("name", "phone", "birth_date")}
        if not allowed:
            return False
        return User.update(**allowed).where(User.id == user_id).execute() > 0

    @staticmethod
    def update_email(user_id: int, email: str) -> bool:
        """Change l'e-mail ; il devra être revérifié."""
        return User.update(email=email, email_verified=False).where(User.id == user_id).execute() > 0

    @staticmethod
    def set_email_verified(user_id: int) -> bool:
        return User.update(email_verified=True).where(User.id == user_id).execute() > 0

    @staticmethod
    def force_delete(user_id: int) -> bool:
        deleted = User.delete().where(User.id == user_id).execute()
        return deleted > 0
