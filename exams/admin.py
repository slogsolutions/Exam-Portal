from django.contrib import admin
from .models import ExamDayAvailability, Shift

@admin.register(ExamDayAvailability)
class ExamDayAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['date']  # show date column
    filter_horizontal = ['categories']  # if you have ManyToMany categories

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['center', 'date', 'start_time', 'capacity']
    list_filter = ['center','date']