from django.contrib import admin
from .models import ExamDayAvailability, Shift

@admin.register(ExamDayAvailability)
class ExamDayAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['date']
    filter_horizontal = ['categories']  # if categories is ManyToMany

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['center', 'date', 'start_time', 'capacity']
