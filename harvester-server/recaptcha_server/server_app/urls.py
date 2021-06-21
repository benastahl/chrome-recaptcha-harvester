from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.waiting_for_captcha),
    path('loading', views.load)
]
