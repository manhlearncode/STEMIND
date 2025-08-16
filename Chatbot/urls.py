from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('upload/', views.upload_file, name='upload_file'),
    path('user-profile/', views.user_profile_view, name='user_profile'),
    path('list-users/', views.list_users_view, name='list_users'),
    path('page/', views.chatbot_page, name='chatbot_page'),
    path('download-file/<int:file_id>/', views.download_chat_file, name='download_chat_file'),
    path('test-download/<int:file_id>/', views.test_download, name='test_download'),
    path('files/', views.list_chat_files, name='list_chat_files'),
    path('files/<str:session_id>/', views.list_chat_files, name='list_session_files'),
]