from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import CandidateProfile

@admin.register(CandidateProfile)
class CandidateAdmin(ImportExportModelAdmin):
    list_display = ("army_no", "name", "rank", "trade", "category", "center")
    search_fields = ("army_no", "name")
    list_filter = ("category", "center", "trade")
