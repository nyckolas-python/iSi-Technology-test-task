from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Thread, Message

class ThreadAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'get_participants', 'created', 'updated')
    # Filters for the sidebar
    list_filter = ('created', 'updated')
    # Enable search by participant's username
    search_fields = ('participants__username',)
    # Default ordering
    ordering = ('-created',)

    def get_participants(self, obj):
        """
        Returns a comma-separated list of participant usernames.
        """
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = _('Participants')

class MessageAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('id', 'thread', 'sender', 'short_text', 'is_read', 'created')
    # Filters for the sidebar
    list_filter = ('is_read', 'sender', 'thread', 'created')
    # Enable search by message text and sender's username
    search_fields = ('text', 'sender__username')
    # Default ordering
    ordering = ('-created',)
    # Add custom admin actions
    actions = ['mark_as_read', 'mark_as_unread']

    def short_text(self, obj):
        """
        Returns a shortened version of the message text (first 50 characters).
        """
        return obj.text[:50]
    short_text.short_description = _('Text')

    @admin.action(description=_("Mark selected messages as read"))
    def mark_as_read(self, request, queryset):
        """
        Admin action to mark selected messages as read.
        """
        updated = queryset.update(is_read=True)
        self.message_user(request, _(f"{updated} messages marked as read."))

    @admin.action(description=_("Mark selected messages as unread"))
    def mark_as_unread(self, request, queryset):
        """
        Admin action to mark selected messages as unread.
        """
        updated = queryset.update(is_read=False)
        self.message_user(request, _(f"{updated} messages marked as unread."))

# Register the models with their respective admin classes
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
