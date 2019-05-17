"""DB_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'Game_2048'
urlpatterns = [
    path('', views.index, name='index'),
    path('check_login/', views.check_login, name='check_login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('check_register/', views.check_register, name='check_register'),
    path('playing/', views.playing, name='playing'),
    path('submit_score/', views.submit_score, name='submit_score'),
    path('message_board/', views.message_board, name='message_board'),
    path('personal/', views.personal, name='personal'),
]
