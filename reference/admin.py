from django.contrib import admin
from .models import Trade, Level, Skill, QF, Category, Qualification

admin.site.register([Trade, Level, Skill, QF, Category, Qualification])
