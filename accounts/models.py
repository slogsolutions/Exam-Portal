
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Roles(models.TextChoices):
        NODAL_ADMIN = "NODAL_ADMIN", "Nodal Admin"
        CENTER_ADMIN = "CENTER_ADMIN", "Center Admin"
        EVALUATOR = "EVALUATOR", "Evaluator"
        VETTER = "VETTER", "Vetting Authority"
        RESULT_UPLOADER = "RESULT_UPLOADER", "Result Uploader"
        CANDIDATE = "CANDIDATE", "Candidate"

    role = models.CharField(max_length=32, choices=Roles.choices, default=Roles.CANDIDATE, db_index=True)

    # optional link to a center (set later; FK declared here to avoid circular imports at runtime)
    center = models.ForeignKey(
        "centers.Center",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
