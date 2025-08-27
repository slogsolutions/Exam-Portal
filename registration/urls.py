from django.urls import path

from registration import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
     path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.candidate_dashboard, name="candidate_dashboard"),
]
