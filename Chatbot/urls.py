from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot page
    path('', views.chatbot_view, name='chatbot'),
    
    # API endpoints
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('upload/', views.upload_file, name='upload_file'),
    
    # Get message endpoint (legacy)
    path('get-message/', views.get_message, name='get_message'),
]