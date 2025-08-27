# results/models.py
from django.db import models
from exams.models import ExamAttempt

class CandidateResult(models.Model):
    attempt = models.OneToOneField(ExamAttempt, on_delete=models.CASCADE, related_name="result")
    total_exam_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    practical_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    viva_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    vetted = models.BooleanField(default=False)
    vetted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Result for {self.attempt.assignment.candidate}"
