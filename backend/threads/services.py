import logging
from typing import Optional, Type

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, QuerySet

from .models import Message, Thread

logger = logging.getLogger(__name__)

User = get_user_model()


class ThreadValidationError(Exception):
    def __init__(self):
        self.message = "Thread must have exactly 2 participants"
        super().__init__(self.message)


class ThreadService:
    model: Type[Thread] = Thread

    @staticmethod
    def get_thread_by_participants(user_id: int, participant_id: int) -> Optional[Thread]:
        """
        Get existing thread between two users
        Args:
            user_id: Current user ID
            participant_id: Other participant ID
        Returns:
            Thread if exists, None otherwise
        """
        return (
            Thread.objects.filter(participants__id__in=[user_id, participant_id])
            .annotate(participant_count=Count('participants'))
            .filter(participant_count=2)
            .select_related('creator')
            .prefetch_related('participants')
            .first()
        )

    @staticmethod
    def create_thread_with_participant(
        creator_id: int,
        participant_id: int
    ) -> Thread:
        """
        Create a new thread between creator and participant
        Args:
            creator_id: User who creates the thread
            participant_id: User to create thread with
        Returns:
            Created Thread instance
        """
        with transaction.atomic():
            thread = Thread.objects.create(creator_id=creator_id)
            thread.participants.set([creator_id, participant_id])
            logger.info(
                f"Created new thread {thread.id} between users {creator_id} and {participant_id}"
            )
            return thread

    @staticmethod
    def get_user_threads(user_id: int) -> QuerySet[Thread]:
        """Get all user threads with optimized queries"""
        return (
            Thread.objects.filter(participants__id=user_id)
            .select_related('creator')
            .prefetch_related('participants')
            .order_by('-updated')
        )


class MessageService:
    model: Type[Message] = Message

    @staticmethod
    def create_message(sender_id: int, thread_id: int, text: str) -> Message:
        """Create a new message"""
        with transaction.atomic():
            message = Message.objects.create(
                sender_id=sender_id, thread_id=thread_id, text=text
            )
            logger.info(f"Created new message {message.id} in thread {thread_id}")
            return message

    @staticmethod
    def check_thread_participant(thread_id: int, user_id: int) -> bool:
        """Check if user is thread participant (optimized query)"""
        return Thread.objects.filter(
            id=thread_id,
            participants__id=user_id
        ).exists()

    @staticmethod
    def mark_messages_as_read(user_id: int, message_ids: list[int]) -> None:
        """
        Mark messages as read
        Args:
            user_id: ID of user marking messages as read
            message_ids: List of message IDs to mark as read
        Note:
            Only message recipient or admin can mark messages as read
        """
        with transaction.atomic():
            Message.objects.filter(
                id__in=message_ids,
                thread__participants__id=user_id,  # User must be thread participant
                is_read=False,  # Only update unread messages
                sender_id__ne=user_id,  # User must not be sender
            ).update(is_read=True)

    @staticmethod
    def can_mark_message_as_read(user: User, message: Message) -> bool:
        """
        Check if user can mark message as read
        Args:
            user: User trying to mark message as read
            message: Message to mark as read
        Returns:
            True if user is message recipient or admin
        """
        return user.is_staff or (
            message.sender_id != user.id and
            message.thread.participants.filter(id=user.id).exists()
        )

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get unread messages count (optimized query)"""
        return Message.objects.filter(
            thread__participants__id=user_id,
            is_read=False
        ).exclude(
            sender_id=user_id
        ).count()

    @staticmethod
    def get_thread_messages(thread_id: int) -> QuerySet[Message]:
        """Get all thread messages with optimized queries"""
        return (
            Message.objects.filter(thread_id=thread_id)
            .select_related('sender')
            .order_by('created')
        )


class UserService:
    @staticmethod
    def get_user_threads(user_id: int) -> QuerySet[Thread]:
        """
        Get all user threads with optimized queries
        Args:
            user_id: User ID to get threads for
        Returns:
            QuerySet of threads
        """
        return (
            Thread.objects.filter(participants__id=user_id)
            .select_related('creator')
            .prefetch_related('participants')
            .order_by('-updated')
        )

    @staticmethod
    def get_user_unread_messages_count(user_id: int) -> int:
        """
        Get number of unread messages for user
        Args:
            user_id: User ID to get count for
        Returns:
            Number of unread messages
        """
        return Message.objects.filter(
            thread__participants__id=user_id,
            is_read=False
        ).exclude(
            sender_id=user_id
        ).count()
