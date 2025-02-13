from django.urls import path

from .views import (MessageDetailAPI, MessageListCreateAPI, ThreadDetailAPI,
                    ThreadListCreateAPI, UserThreadListAPI,
                    UserUnreadMessagesCountAPI)

app_name = 'threads'

urlpatterns = [
    # Thread endpoints
    path('threads/', ThreadListCreateAPI.as_view(), name='thread-list-create'),
    path('threads/<int:pk>/', ThreadDetailAPI.as_view(), name='thread-detail'),

    # Messages in thread endpoints
    path('threads/<int:thread_id>/messages/', MessageListCreateAPI.as_view(), name='message-list-create'),
    path('threads/<int:thread_id>/messages/<int:pk>/', MessageDetailAPI.as_view(), name='message-detail'),

    # User specific endpoints
    path('users/<int:user_id>/threads/', UserThreadListAPI.as_view(), name='user-threads'),
    path('users/<int:user_id>/unread-messages-count/', UserUnreadMessagesCountAPI.as_view(), name='user-unread-messages-count'),
]