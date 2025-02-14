from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from threads.models import Thread, Message
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        # Create users
        admin, created = User.objects.get_or_create(
            username='admin',
            email='admin@example.com',
            defaults={'password': make_password('admin'), 'is_staff': True, 'is_superuser': True}
        )

        user1, created = User.objects.get_or_create(
            username='user1',
            email='user1@example.com',
            defaults={'password': make_password('user1')}
        )

        user2, created = User.objects.get_or_create(
            username='user2',
            email='user2@example.com',
            defaults={'password': make_password('user2')}
        )

        # Create threads
        thread1 = Thread.objects.create()
        thread1.participants.set([user1, user2])

        thread2 = Thread.objects.create()
        thread2.participants.set([user1, user2])

        # Create messages
        Message.objects.create(
            thread=thread1,
            sender=user1,
            text="Hello from user1!",
            created=timezone.now()
        )

        Message.objects.create(
            thread=thread1,
            sender=user2,
            text="Hi user1!",
            created=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS('Test data created successfully'))
