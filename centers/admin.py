from django.contrib import admin
from .models import Center

@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ("comd", "exam_Center", "district", "state", "capacity", "is_active")
    list_filter = ("state", "is_active")
    search_fields = ("comd", "exam_Center", "district", "state")
