from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_dashboard, name='chat-dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_chat, name='create_chat'),
    path('room/<int:chat_id>/', views.chatroom_detail, name='chatroom_detail'),
]