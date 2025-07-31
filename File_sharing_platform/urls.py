from . import views
from django.urls import path

urlpatterns = [
    path("", views.home, name="home"),
    path("enter/", views.enter, name="enter"),
    path("register/", views.register, name="register"),
    path("logout/", views.user_logout, name="logout"),
    path("category/<str:category_name>/", views.posts_by_category, name='posts_by_category'),
    path("file/<str:title>/", views.file_detail, name='file_detail'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('upload/', views.upload_file, name='upload_file'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    path('favorites/', views.user_favorites, name='user_favorites'),
    path('toggle-favorite/<int:file_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('about/', views.about, name='about'),
    path('api/files/', views.file_list_api, name='file_list_api'),
    path('chatbot-page/', views.chatbot_page, name='chatbot_page'),
]