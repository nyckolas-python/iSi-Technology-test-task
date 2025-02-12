from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_participants_count(value):
    if value.count() > 2:
        raise ValidationError(
            _('Thread cannot have more than 2 participants.'),
            code='invalid_participants_count'
        )

class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads', validators=[validate_participants_count])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
        constraints = [
            models.CheckConstraint(
                check=models.Q(participants__lt=3),
                name='max_two_participants'
            )
        ]

    def clean(self):
        super().clean()
        if self.participants.count() > 2:
            raise ValidationError(_('Thread cannot have more than 2 participants.'))

    def __str__(self):
        return f"Thread - {self.id}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Message - {self.id} - {self.sender} - {self.thread}"
