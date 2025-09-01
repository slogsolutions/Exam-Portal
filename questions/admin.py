from django.contrib import admin
from .models import Question, QuestionPaper, PaperQuestion, QuestionUpload
from .forms import QuestionUploadForm
from django.contrib import messages

class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 1
    autocomplete_fields = ["question"]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "part", "marks", "trade", "is_active", "created_at")
    list_filter = ("part", "trade", "is_active", "created_at")
    search_fields = ("text",)
    list_per_page = 50
    ordering = ("-created_at",)

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "upload", "is_common", "trade", "active_from", "active_to")
    list_filter = ("is_common", "trade", "active_from")
    inlines = [PaperQuestionInline]
    search_fields = ("title",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.upload:
            # Auto-link questions that were imported from this upload
            questions = Question.objects.filter(created_at__gte=obj.upload.uploaded_at)
            created_count = 0
            
            for i, q in enumerate(questions, start=1):
                paper_question, created = PaperQuestion.objects.get_or_create(
                    paper=obj,
                    question=q,
                    defaults={"order": i}
                )
                if created:
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f"Linked {created_count} questions to this paper")

@admin.register(QuestionUpload)
class QuestionUploadAdmin(admin.ModelAdmin):
    form = QuestionUploadForm
    list_display = ("file", "uploaded_at", "get_questions_count")
    search_fields = ("file",)
    readonly_fields = ("uploaded_at",)
    list_per_page = 20
    ordering = ("-uploaded_at",)

    def get_questions_count(self, obj):
        """Show how many questions were imported from this upload"""
        if obj.uploaded_at:
            count = Question.objects.filter(created_at__gte=obj.uploaded_at).count()
            return f"{count} questions"
        return "0 questions"
    get_questions_count.short_description = "Imported Questions"

    def save_model(self, request, obj, form, change):
        # Ensure password is saved
        if "decryption_password" in form.cleaned_data:
            obj.decryption_password = form.cleaned_data["decryption_password"]
        
        super().save_model(request, obj, form, change)
        
        if not change:  # Only for new uploads
            messages.info(request, 
                "File uploaded successfully. Questions will be imported automatically.")

    def response_add(self, request, obj, post_url_redirect=None):
        response = super().response_add(request, obj, post_url_redirect)
        
        # Add success message with import status
        if obj:
            try:
                import time
                time.sleep(1)  # Give signals time to process
                
                questions_count = Question.objects.filter(
                    created_at__gte=obj.uploaded_at
                ).count()
                
                if questions_count > 0:
                    messages.success(request, 
                        f"Successfully imported {questions_count} questions from {obj.file.name}")
                else:
                    messages.warning(request, 
                        "Upload completed but no questions were imported. "
                        "Please check the file format and password.")
            except Exception as e:
                messages.error(request, f"Upload completed but there was an error: {e}")
        
        return response