from peewee import DoesNotExist
from ..models import Conversation, Message, User


class ConversationRepo:
    @staticmethod
    def get_or_create_for_trip(trip_id: int, initiator_id: int, recipient_id: int) -> tuple[Conversation, bool]:
        """Retourne la conversation existante ou en crée une nouvelle."""
        existing = (
            Conversation.select()
            .where(
                (Conversation.trip == trip_id)
                & (
                    ((Conversation.initiator == initiator_id) & (Conversation.recipient == recipient_id))
                    | ((Conversation.initiator == recipient_id) & (Conversation.recipient == initiator_id))
                )
            )
            .first()
        )
        if existing:
            return existing, False
        conv = Conversation.create(initiator=initiator_id, recipient=recipient_id, trip=trip_id)
        return conv, True

    @staticmethod
    def get_or_create_for_parcel(parcel_id: int, initiator_id: int, recipient_id: int) -> tuple[Conversation, bool]:
        existing = (
            Conversation.select()
            .where(
                (Conversation.parcel == parcel_id)
                & (
                    ((Conversation.initiator == initiator_id) & (Conversation.recipient == recipient_id))
                    | ((Conversation.initiator == recipient_id) & (Conversation.recipient == initiator_id))
                )
            )
            .first()
        )
        if existing:
            return existing, False
        conv = Conversation.create(initiator=initiator_id, recipient=recipient_id, parcel=parcel_id)
        return conv, True

    @staticmethod
    def get_by_id(conv_id: int) -> Conversation | None:
        try:
            return Conversation.get_by_id(conv_id)
        except DoesNotExist:
            return None

    @staticmethod
    def list_for_user(user_id: int) -> list[Conversation]:
        return list(
            Conversation.select()
            .where(
                (Conversation.initiator == user_id) | (Conversation.recipient == user_id)
            )
            .order_by(Conversation.created_at.desc())
        )

    @staticmethod
    def send_message(conv_id: int, sender_id: int, content: str) -> Message:
        return Message.create(conversation=conv_id, sender=sender_id, content=content)

    @staticmethod
    def list_messages(conv_id: int) -> list[Message]:
        return list(
            Message.select()
            .where(Message.conversation == conv_id)
            .order_by(Message.created_at)
        )

    @staticmethod
    def mark_read(conv_id: int, user_id: int) -> None:
        """Marque comme lus tous les messages envoyés par l'autre partie."""
        Message.update(is_read=True).where(
            (Message.conversation == conv_id) & (Message.sender != user_id) & (Message.is_read == False)
        ).execute()

    @staticmethod
    def unread_in_conversation(conv_id: int, user_id: int) -> int:
        """Messages de l'autre partie que cet utilisateur n'a pas encore lus dans la conversation."""
        return (
            Message.select()
            .where((Message.conversation == conv_id) & (Message.sender != user_id) & (Message.is_read == False))
            .count()
        )

    @staticmethod
    def unread_count(user_id: int) -> int:
        """Nombre total de messages non lus pour cet utilisateur."""
        return (
            Message.select()
            .join(Conversation)
            .where(
                ((Conversation.initiator == user_id) | (Conversation.recipient == user_id))
                & (Message.sender != user_id)
                & (Message.is_read == False)
            )
            .count()
        )
