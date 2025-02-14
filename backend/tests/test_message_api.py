import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMessageAPI:
    def test_create_message(self, authenticated_client, thread):
        """
        Test creating a new message in a thread.
        Expected result: The message is created successfully with status 201.
        """
        url = reverse("threads:message-list-create", kwargs={"thread_id": thread.id})
        data = {"text": "Test message"}

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["text"] == "Test message"

    def test_list_messages(self, authenticated_client, thread, message):
        """
        Test retrieving a list of messages in a thread.
        Expected result: The request returns status 200 and includes one message.
        """
        url = reverse("threads:message-list-create", kwargs={"thread_id": thread.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_mark_message_as_read(self, api_client, thread, message, user2):
        """
        Test marking a specific message as read by another participant in the thread.
        Expected result: The request returns status 204, and the message is marked as read.
        """
        api_client.force_authenticate(user=user2)
        url = reverse(
            "threads:message-detail", kwargs={"thread_id": thread.id, "pk": message.id}
        )

        response = api_client.patch(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        message.refresh_from_db()
        assert message.is_read == True

    def test_mark_own_message_as_read(self, authenticated_client, thread, message):
        """
        Test attempting to mark one's own message as read.
        Expected result: The request returns status 403 (forbidden).
        """
        url = reverse(
            "threads:message-detail", kwargs={"thread_id": thread.id, "pk": message.id}
        )

        response = authenticated_client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_mark_all_messages_as_read(self, api_client, thread, message, user2):
        """
        Test marking all messages in a thread as read.
        Expected result: The request returns status 204, and all messages are marked as read.
        """
        api_client.force_authenticate(user=user2)
        url = reverse("threads:message-list-create", kwargs={"thread_id": thread.id})

        response = api_client.patch(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        message.refresh_from_db()
        assert message.is_read == True
