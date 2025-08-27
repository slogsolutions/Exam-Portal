from django.contrib import admin
from .models import Question, QuestionPaper, PaperQuestion

class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "part", "marks", "trade", "level", "skill", "category", "is_active")
    list_filter = ("part", "trade", "level", "skill", "category", "is_active")
    search_fields = ("text",)

@admin.register(QuestionPaper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ("title", "is_common", "trade", "level", "skill", "category", "active_from", "active_to")
    list_filter = ("is_common", "trade", "level", "skill", "category")
    inlines = [PaperQuestionInline]
