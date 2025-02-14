import os

import django
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from threads.models import Message, Thread

# Налаштування Django для тестів
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "isi_app.settings")
django.setup()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="admin"
    )


@pytest.fixture
def user1():
    return User.objects.create_user(
        username="user1", email="user1@example.com", password="user1"
    )


@pytest.fixture
def user2():
    return User.objects.create_user(
        username="user2", email="user2@example.com", password="user2"
    )


@pytest.fixture
def user3():
    return User.objects.create_user(
        username="user3", email="user3@example.com", password="user3"
    )


@pytest.fixture
def authenticated_client(api_client, user1):
    api_client.force_authenticate(user=user1)
    api_client.user = user1
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def thread(user1, user2):
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])
    return thread


@pytest.fixture
def message(thread, user1):
    return Message.objects.create(thread=thread, sender=user1, text="Test message")
