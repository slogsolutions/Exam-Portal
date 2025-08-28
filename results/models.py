# results/models.py
from django.db import models
from questions.models import Question, QuestionPaper
from registration.models import CandidateProfile   # assuming you have this

class CandidateAnswer(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.army_no} - {self.paper.title} - {self.question.id}"
