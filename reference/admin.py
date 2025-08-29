from django.contrib import admin
from .models import Level, Skill, QF, Category, Qualification

admin.site.register([Level, Skill, QF, Category, Qualification])
