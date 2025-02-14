import pytest
from django.urls import reverse
from rest_framework import status
from threads.models import Message, Thread


@pytest.mark.django_db
class TestThreadAPI:
    def test_create_thread(self, authenticated_client, user2):
        """
        Create a new chat with another user.
        Expectation: A thread is created with two participants.
        """
        url = reverse("threads:thread-list-create")
        data = {"participant_id": user2.id}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED, response.data

        # Verify that the response contains both participants
        participants = response.data.get("participants", [])
        assert len(participants) == 2
        participant_ids = [p["id"] for p in participants]
        assert authenticated_client.user.id in participant_ids
        assert user2.id in participant_ids

    def test_create_thread_with_self(self, authenticated_client):
        """
        Attempting to create a chat with oneself should return an error.
        """
        url = reverse("threads:thread-list-create")
        data = {"participant_id": authenticated_client.user.id}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_threads(self, authenticated_client, thread):
        """
        Retrieve a list of threads for the authenticated user.
        """
        url = reverse("threads:thread-list-create")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Ensure pagination is used (response contains 'results' key)
        assert "results" in response.data
        thread_ids = [item["id"] for item in response.data["results"]]
        assert thread.id in thread_ids

    def test_delete_thread(self, authenticated_client, thread):
        """
        Deleting a thread when the user is a participant.
        """
        url = reverse("threads:thread-detail", kwargs={"pk": thread.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Ensure the thread no longer exists
        assert not Thread.objects.filter(id=thread.id).exists()

    def test_delete_thread_not_participant(self, api_client, thread, user3):
        """
        A user who is not a participant should not be able to delete the thread.
        Expectation: 403 Forbidden error.
        """
        api_client.force_authenticate(user=user3)
        url = reverse("threads:thread-detail", kwargs={"pk": thread.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
