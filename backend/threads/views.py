from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (OpenApiParameter, OpenApiResponse,
                                   extend_schema)
from rest_framework import generics, response, status
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.validators import ValidationError

from .models import Message, Thread
from .permissions import IsAdmin, IsParticipant
from .serializers import (MessageCreateSerializer, MessageReadSerializer,
                          ThreadCreateSerializer, ThreadQueryParamsSerializer,
                          ThreadReadSerializer)
from .services import (MessageService, ThreadService, ThreadValidationError,
                       UserService)

__all__ = [
    "ThreadListCreateAPI",
    "ThreadDetailAPI",
    "MessageListCreateAPI",
    "MessageDetailAPI",
    "UserThreadListAPI",
    "UserUnreadMessagesCountAPI",
]


@extend_schema(tags=["threads"])
class ThreadListCreateAPI(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["created"]
    service = ThreadService
    queryset = Thread.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ThreadCreateSerializer
        return ThreadReadSerializer

    def get_queryset(self):
        # This is a workaround for Swagger UI/OpenAPI schema generation.
        # When Swagger is generating API documentation, it creates a fake view instance
        # to introspect the viewset. In this case, we return an empty queryset
        # to prevent unnecessary database queries during schema generation.
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return self.service.get_user_threads(self.request.user.id)

    @extend_schema(
        summary="Get threads list with pagination",
        description="""
        Get a paginated list of threads for the authenticated user.
        Each thread contains information about participants and last message.
        Results can be ordered by creation date and filtered.
        """,
        parameters=[
            OpenApiParameter(
                name="limit",
                description="Number of records per page",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="offset",
                description="Number of records to skip",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="ordering",
                description='Order by field (e.g. "created" or "-created" for descending)',
                required=False,
                type=str,
            ),
        ],
        responses={
            200: ThreadReadSerializer,
            401: OpenApiResponse(description="Unauthorized"),
        },
        operation_id="list_threads",
    )
    def get(self, request, *args, **kwargs):
        ThreadQueryParamsSerializer(data=request.query_params).is_valid(
            raise_exception=True
        )
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new chat thread",
        description="""
        Create a new private chat thread with another user.
        The authenticated user automatically becomes the first participant and creator.
        If a thread between these users already exists, returns the existing thread.
        """,
        request=ThreadCreateSerializer,
        responses={
            201: ThreadReadSerializer,
            400: OpenApiResponse(
                description="Invalid participant_id or attempt to create thread with self"
            ),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Participant not found"),
        },
        operation_id="create_thread",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participant_id = serializer.validated_data["participant_id"]

        # Check if participant exists
        if not User.objects.filter(id=participant_id).exists():
            return response.Response(
                {"detail": "Participant not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Try to get existing thread
            thread = self.service.get_thread_by_participants(
                user_id=request.user.id, participant_id=participant_id
            )

            if thread is None:
                # Create new thread if doesn't exist
                thread = self.service.create_thread_with_participant(
                    creator_id=request.user.id, participant_id=participant_id
                )

            response_data = ThreadReadSerializer(instance=thread).data
            return response.Response(response_data, status=status.HTTP_201_CREATED)

        except ThreadValidationError as e:
            raise ValidationError(e.message)


@extend_schema(tags=["threads"])
class ThreadDetailAPI(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ThreadReadSerializer
    queryset = Thread.objects.all()

    def check_object_permissions(self, request, obj: Thread):
        if not obj.participants.filter(id=request.user.id).exists():
            self.permission_denied(
                request,
                message="You don't have permission to delete this thread",
                code=403,
            )

    @extend_schema(
        summary="Delete chat thread",
        description="""
        Permanently delete a chat thread and all its messages.
        Only thread participants can delete the thread.
        This action cannot be undone.
        """,
        responses={
            204: OpenApiResponse(description="Thread deleted successfully"),
            403: OpenApiResponse(description="Not a thread participant"),
            404: OpenApiResponse(description="Thread not found"),
        },
        operation_id="delete_thread",
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["messages"])
class MessageListCreateAPI(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created"]
    ordering = ["created"]
    service = MessageService()
    # For swagger to work correctly
    queryset = Message.objects.none()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageReadSerializer

    def get_queryset(self):
        # This is a workaround for Swagger UI/OpenAPI schema generation.
        # When Swagger is generating API documentation, it creates a fake view instance
        # to introspect the viewset. In this case, we return an empty queryset
        # to prevent unnecessary database queries during schema generation.
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return self.service.get_thread_messages(self.kwargs["thread_id"])

    @extend_schema(
        summary="Get thread messages with pagination",
        description="""
        Get a paginated list of messages in a specific thread.
        Messages include sender information and read status.
        Results can be ordered by creation date.
        Only thread participants can access messages.
        """,
        parameters=[
            OpenApiParameter(
                name="limit",
                description="Number of records per page",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="offset",
                description="Number of records to skip",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="ordering",
                description='Order by field (e.g. "created" or "-created" for descending)',
                required=False,
                type=str,
            ),
        ],
        responses={
            200: MessageReadSerializer,
            403: OpenApiResponse(description="Not a thread participant"),
            404: OpenApiResponse(description="Thread not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        ThreadQueryParamsSerializer(data=request.query_params).is_valid(
            raise_exception=True
        )
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Send new message to thread",
        description="""
        Create a new message in a specific thread.
        Only thread participants can send messages.
        Message will be marked as unread for other participants.
        Returns the created message with all details.
        """,
        request=MessageCreateSerializer,
        responses={
            201: MessageReadSerializer,
            403: OpenApiResponse(description="Not a thread participant"),
            404: OpenApiResponse(description="Thread not found"),
        },
        operation_id="create_message",
    )
    def post(self, request, *args, **kwargs):
        thread_id = self.kwargs["thread_id"]
        if not self.service.check_thread_participant(thread_id, request.user.id):
            return response.Response(
                {"detail": "You don't have permission to send messages to this thread"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = self.service.create_message(
            sender_id=request.user.id,
            thread_id=thread_id,
            text=serializer.validated_data["text"],
        )

        response_data = MessageReadSerializer(instance=message).data
        return response.Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Mark all thread messages as read",
        description="""
        Mark all messages in the thread as read for the current user.
        Only message recipients or admins can mark messages as read.
        Messages sent by the current user cannot be marked as read.
        """,
        responses={
            204: OpenApiResponse(description="Messages marked as read"),
            403: OpenApiResponse(description="Not a thread participant or message sender"),
            404: OpenApiResponse(description="Thread not found"),
        },
    )
    def patch(self, request, *args, **kwargs):
        """Mark all messages in thread as read"""
        thread_id = self.kwargs["thread_id"]

        # Check if user is thread participant
        if not self.service.check_thread_participant(thread_id, request.user.id):
            return response.Response(
                {"detail": "You don't have permission to mark messages in this thread"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all unread messages in thread where user is not sender
        messages = Message.objects.filter(
            thread_id=thread_id,
            is_read=False
        ).exclude(sender_id=request.user.id)

        message_ids = list(messages.values_list("id", flat=True))
        self.service.mark_messages_as_read(request.user.id, message_ids)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["messages"])
class MessageDetailAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageReadSerializer
    service = MessageService()
    queryset = Message.objects.all()

    @extend_schema(
        summary="Mark specific message as read",
        description="""
        Mark a single message as read for the current user.
        Only message recipients or admins can mark messages as read.
        Messages sent by the current user cannot be marked as read.
        Returns 404 if message doesn't belong to thread.
        """,
        responses={
            204: OpenApiResponse(description="Message marked as read"),
            403: OpenApiResponse(description="Not a recipient or message sender"),
            404: OpenApiResponse(description="Message not found or doesn't belong to thread"),
        },
    )
    def patch(self, request, thread_id, pk):
        """Mark specific message as read"""
        message = self.get_object()

        if message.thread_id != thread_id:
            return response.Response(
                {"detail": "Message does not belong to this thread"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user can mark message as read
        if not self.service.can_mark_message_as_read(request.user, message):
            return response.Response(
                {"detail": "You don't have permission to mark this message as read"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.service.mark_messages_as_read(request.user.id, [pk])
        return response.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["users"])
class UserThreadListAPI(generics.ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsParticipant,
    )
    serializer_class = ThreadReadSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["created"]
    service = UserService
    # For swagger to work correctly
    queryset = Thread.objects.none()

    def get_queryset(self):
        # This is a workaround for Swagger UI/OpenAPI schema generation.
        # When Swagger is generating API documentation, it creates a fake view instance
        # to introspect the viewset. In this case, we return an empty queryset
        # to prevent unnecessary database queries during schema generation.
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        return self.service.get_user_threads(self.kwargs["user_id"])

    @extend_schema(
        summary="Get user's threads",
        description="""
        Get a paginated list of threads for a specific user.
        Access is restricted to:
        - The user themselves
        - Admin users
        Each thread contains information about participants and last message.
        Results can be ordered by creation date.
        """,
        parameters=[
            OpenApiParameter(
                name="limit",
                description="Number of records per page",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="offset",
                description="Number of records to skip",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="ordering",
                description='Order by field (e.g. "created" or "-created" for descending)',
                required=False,
                type=str,
            ),
        ],
        responses={
            200: ThreadReadSerializer,
            403: OpenApiResponse(description="Not authorized to view these threads"),
            404: OpenApiResponse(description="User not found"),
        },
    )
    def get(self, request, *args, **kwargs):
        ThreadQueryParamsSerializer(data=request.query_params).is_valid(
            raise_exception=True
        )
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["users"])
class UserUnreadMessagesCountAPI(generics.GenericAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsParticipant,
    )
    serializer_class = MessageReadSerializer
    service = UserService()

    @extend_schema(
        summary="Get user's unread messages count",
        description="""
        Get the total number of unread messages for a specific user.
        Access is restricted to:
        - The user themselves
        - Admin users
        This includes messages from all threads where user is a participant.
        Excludes messages sent by the user.
        """,
        responses={
            200: OpenApiResponse(
                description="Unread messages count",
                response={
                    "type": "object",
                    "properties": {"count": {"type": "integer"}},
                },
            ),
            403: OpenApiResponse(description="Not authorized to view this count"),
            404: OpenApiResponse(description="User not found"),
        },
    )
    def get(self, request, user_id):
        count = self.service.get_user_unread_messages_count(user_id)
        return response.Response({"count": count})
