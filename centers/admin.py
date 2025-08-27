from django.contrib import admin
from .models import Center

@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "district", "state", "capacity", "is_active")
    list_filter = ("state", "is_active")
    search_fields = ("code", "name", "district", "state")
