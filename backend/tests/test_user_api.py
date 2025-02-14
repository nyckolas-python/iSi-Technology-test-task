import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestUserAPI:
    def test_list_user_threads(self, authenticated_client, thread, user1):
        """
        Test retrieving a list of threads for the authenticated user.
        Expected result: The request returns status 200 and includes one thread.
        """
        url = reverse("threads:user-threads", kwargs={"user_id": user1.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_list_other_user_threads(self, authenticated_client, thread, user2):
        """
        Test retrieving a list of threads for another user.
        Expected result: The request returns status 403 (forbidden).
        """
        url = reverse("threads:user-threads", kwargs={"user_id": user2.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_list_other_user_threads(self, admin_client, thread, user1):
        """
        Test an admin retrieving a list of threads for another user.
        Expected result: The request returns status 200 and includes one thread.
        """
        url = reverse("threads:user-threads", kwargs={"user_id": user1.id})

        response = admin_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_get_unread_messages_count(self, api_client, thread, message, user2):
        """
        Test retrieving the unread messages count for a user.
        Expected result: The request returns status 200 with the correct unread message count.
        """
        api_client.force_authenticate(user=user2)
        url = reverse(
            "threads:user-unread-messages-count", kwargs={"user_id": user2.id}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
