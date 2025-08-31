from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from exams.models import Shift   # ✅ keep Shift


class CandidateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile"
    )

    # ✅ Personal details
    army_no = models.CharField(max_length=50, unique=True)
    
    rank = models.CharField(max_length=50)
    trade = models.CharField(max_length=100, blank=True, null=True)

    name = models.CharField(max_length=150)
    dob = models.DateField(verbose_name="Date of Birth")
    doe = models.DateField(verbose_name="Date of Enrolment")
    aadhar_number = models.CharField(max_length=12, blank=True)
    father_name = models.CharField(max_length=150)
    photograph = models.ImageField(upload_to="photos/", blank=True, null=True)

    # ✅ Exam details
    qualification = models.CharField(max_length=150)
    nsqf_level = models.CharField(max_length=50, blank=True)
    exam_center = models.CharField(max_length=150, blank=True, null=True)

    training_center = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    duration = models.CharField(max_length=50, blank=True)
    credits = models.CharField(max_length=50, blank=True)

    # ✅ Admin-side fields
    viva_marks = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    practical_marks = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def can_start_exam(self):
        if not self.shift:
            return False
        shift_datetime = datetime.combine(self.shift.date, self.shift.start_time)
        shift_datetime = timezone.make_aware(shift_datetime, timezone.get_current_timezone())
        return timezone.now() >= shift_datetime

    def __str__(self):
        return f"{self.army_no} - {self.name}"
