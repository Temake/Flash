from django.urls import path
from .views import *

urlpatterns = [
    path('', ConversationListCreateView.as_view(), name='conversation_list'),
    path('<int:conversation_id>/messages/', MessageListCreateView.as_view(), name='message_list_create'),
    path('<int:conversation_id>/messages/<int:pk>/', MessageRetrieveDestroyView.as_view(), name='message_detail_destroy'),
]
    