from django.db import models
from reference.models import Level, Skill, QF, Category


class Question(models.Model):
    class Part(models.TextChoices):
        A = "A", "Part A - MCQ"
        B = "B", "Part B - True/False"
        C = "C", "Part C - Fill in the blanks"
        D = "D", "Part D - Short answer (50 words)"
        E = "E", "Part E - Long answer (100-120 words)"

    text = models.TextField()
    part = models.CharField(max_length=1, choices=Part.choices)  # required
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    # ✅ For objective (A,B,C)
    options = models.JSONField(blank=True, null=True)         # {"choices": ["A","B","C","D"]}
    correct_answer = models.JSONField(blank=True, null=True)  # "B" or True or "Delhi"

    # ✅ For descriptive (D,E) → just `text` + `marks` + expected answer
    # stored in correct_answer if provided

    # Metadata
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True)
    qf = models.ForeignKey(QF, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_part_display()}] {self.text[:60]}..."


class QuestionUpload(models.Model):
    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class QuestionPaper(models.Model):
    title = models.CharField(max_length=150)
    is_common = models.BooleanField(default=False)
    level = models.ForeignKey(Level, on_delete=models.PROTECT, null=True, blank=True)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, null=True, blank=True)
    qf = models.ForeignKey(QF, on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)

    active_from = models.DateField(null=True, blank=True)
    active_to = models.DateField(null=True, blank=True)
    upload = models.ForeignKey(QuestionUpload, on_delete=models.SET_NULL, null=True, blank=True)
    questions = models.ManyToManyField(Question, through="PaperQuestion")

    def __str__(self):
        return self.title


class PaperQuestion(models.Model):
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("paper", "question")
        ordering = ["order", "id"]



