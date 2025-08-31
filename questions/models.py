from django.db import models
from django.core.exceptions import ValidationError
from reference.models import Trade

def validate_dat_file(value):
    """Simple validation - only check file extension"""
    if not value.name.lower().endswith(".dat"):
        raise ValidationError("Only .dat files are allowed.")
    # REMOVED file content reading to avoid I/O errors

class Question(models.Model):
    class Part(models.TextChoices):
        A = "A", "Part A - MCQ (Single Choice)"
        B = "B", "Part B - MCQ (Multiple Choice)"
        C = "C", "Part C - MCQ (Other format)"
        D = "D", "Part D - Fill in the blanks"
        E = "E", "Part E - Long answer (100-120 words)"
        F = "F", "Part F - True/False"

    text = models.TextField()
    part = models.CharField(max_length=1, choices=Part.choices)
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.JSONField(blank=True, null=True)
    trade = models.ForeignKey(Trade, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"[{self.get_part_display()}] {self.text[:60]}..."

class QuestionUpload(models.Model):
    file = models.FileField(upload_to="uploads/", validators=[validate_dat_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    decryption_password = models.CharField(max_length=255,default="default123")

    def _str_(self):
        return self.file.name

class QuestionPaper(models.Model):
    title = models.CharField(max_length=150)
    is_common = models.BooleanField(default=False)
    
    trade = models.ForeignKey(Trade, on_delete=models.PROTECT, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True,help_text="Enter exam duration in format HH:MM:SS (e.g., 01:30:00 for 1h30m)")
    active_from = models.DateField(null=True, blank=True)
    active_to = models.DateField(null=True, blank=True)
    upload = models.ForeignKey(QuestionUpload, on_delete=models.SET_NULL, null=True, blank=True)
    questions = models.ManyToManyField(Question, through="PaperQuestion")

    def _str_(self):
        return self.title

class PaperQuestion(models.Model):
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("paper", "question")
        ordering = ["order", "id"]