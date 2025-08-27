# evaluation/models.py
from django.db import models
from django.conf import settings
from exams.models import Answer

class EvaluatorAssignment(models.Model):
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evaluator_assignments")
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE, related_name="evaluator_assignment")
    assigned_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evaluator} -> Answer#{self.answer_id}"
