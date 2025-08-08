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
]