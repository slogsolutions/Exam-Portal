from django.urls import path
from .views import register_candidate

urlpatterns = [
    path("register/", register_candidate, name="register_candidate"),
]
