from django.db import models
from django.conf import settings
from reference.models import Trade, Level, Skill, QF, Qualification, Category
from centers.models import Center
from exams.models import Shift   # ✅ Import Shift
from django.utils import timezone
from datetime import datetime

class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")

    army_no = models.CharField(max_length=50, unique=True)
    rank = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    trade = models.ForeignKey(Trade, on_delete=models.PROTECT)
    dob = models.DateField(verbose_name="Date of Birth")
    father_name = models.CharField(max_length=150)
    enrolment_no = models.CharField(max_length=100, blank=True)
    doe = models.DateField(verbose_name="Date of Enrolment")
    aadhar_number = models.CharField(max_length=12, blank=True)
    unit = models.CharField(max_length=120)
    fmn_bde = models.CharField("Fmn (Bde)", max_length=120, blank=True)
    fmn_div = models.CharField("Fmn (Div)", max_length=120, blank=True)
    fmn_corps = models.CharField("Fmn (Corps)", max_length=120, blank=True)
    fmn_comd = models.CharField("Fmn (Comd)", max_length=120, blank=True)
    trg_centre = models.CharField("Training Centre", max_length=150, blank=True)

    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT)
    level_of_qualification = models.ForeignKey(Level, on_delete=models.PROTECT, related_name="candidates_level")
    nsqf_level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name="candidates_nsqf")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    qf = models.ForeignKey(QF, on_delete=models.PROTECT)

    photograph = models.ImageField(upload_to="photos/", blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    center = models.ForeignKey(Center, on_delete=models.PROTECT)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, null=True, blank=True)   # ✅ New Field

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
