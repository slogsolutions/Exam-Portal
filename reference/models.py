# reference/models.py
from django.db import models

# class Trade(models.Model):
#     name = models.CharField(max_length=120, unique=True)
#     code = models.CharField(max_length=30, unique=True)

#     def __str__(self): return f"{self.code} - {self.name}"

class Level(models.Model):
    number = models.PositiveSmallIntegerField()  # e.g., 1..10
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("number", "name")

    def __str__(self): return f"Level {self.number} ({self.name})"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class QF(models.Model):
    name = models.CharField(max_length=120, unique=True)  # Qualification Framework name/descriptor
    def __str__(self): return self.name

class Trade(models.Model):
    """
    14 categories total (we'll seed later).
    """
    name = models.CharField(max_length=80, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self): return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name = "Trade"
        verbose_name_plural = "Trades"

class Qualification(models.Model):
    name = models.CharField(max_length=150, unique=True)
    def __str__(self): return self.name
