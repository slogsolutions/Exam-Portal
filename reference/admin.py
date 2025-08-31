from django.contrib import admin
from .models import Level, Skill, QF, Trade, Qualification

admin.site.register([Level, Skill, QF, Trade, Qualification])
