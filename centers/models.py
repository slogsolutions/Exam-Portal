# centers/models.py
from django.db import models

class Center(models.Model):
    comd = models.CharField(max_length=20,unique=False,blank=True)
    exam_Center = models.CharField(max_length=150,blank=True)
    conducting_Fmn = models.CharField(max_length=150,blank=True)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveSmallIntegerField(default=40)  # per shift
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.comd} - {self.exam_Center} ({self.capacity})"
