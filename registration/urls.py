from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.register_candidate, name="register_candidate"),
     path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.candidate_dashboard, name="candidate_dashboard"),
    path("exam_interface/", views.exam_interface, name="exam_interface"),  # New URL pattern
    path("export-candidate/<int:candidate_id>/", views.export_candidate_json, name="export_candidate_json"),

]
