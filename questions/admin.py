from django.contrib import admin
from .models import Question, QuestionPaper, PaperQuestion, QuestionUpload
from django import forms
from .services import is_encrypted_dat, decrypt_dat_content
import pickle

class QuestionUploadForm(forms.ModelForm):
    decryption_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter decryption password'}),
        help_text="Password required for encrypted DAT files"
    )

    class Meta:
        model = QuestionUpload
        fields = ['file', 'decryption_password']

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        password = cleaned_data.get('decryption_password')
        
        if file and password:
            try:
                # Store file content in memory for validation
                file_content = b''
                for chunk in file.chunks():
                    file_content += chunk
                
                # Check if file is encrypted
                if not is_encrypted_dat(file_content):
                    raise forms.ValidationError(
                        "This file is not encrypted. Only encrypted DAT files are accepted."
                    )
                
                # ✅ ADDED: Validate the password by attempting decryption
                try:
                    # Try to decrypt a small portion to validate password
                    decrypt_dat_content(file_content, password)
                    # If we get here, password is correct
                    
                except ValueError as e:
                    raise forms.ValidationError(f"Invalid password: {e}")
                
                # Store the file content in cleaned_data for later use
                cleaned_data['file_content'] = file_content
                
            except Exception as e:
                raise forms.ValidationError(f"Error reading file: {e}")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Password is already set from form data
        
        if commit:
            instance.save()
        return instance

class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 1
    autocomplete_fields = ["question"]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "part", "marks", "level", "skill", "trade", "is_active")
    list_filter = ("part", "level", "skill", "trade", "is_active")
    search_fields = ("text",)

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "upload", "is_common", "level", "skill", "trade", "active_from", "active_to")
    list_filter = ("is_common", "level", "skill", "trade")
    inlines = [PaperQuestionInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.upload:
            questions = Question.objects.filter(created_at__gte=obj.upload.uploaded_at)
            for i, q in enumerate(questions, start=1):
                PaperQuestion.objects.get_or_create(
                    paper=obj,
                    question=q,
                    defaults={"order": i}
                )

@admin.register(QuestionUpload)
class QuestionUploadAdmin(admin.ModelAdmin):
    form = QuestionUploadForm
    list_display = ("file", "uploaded_at")
    search_fields = ("file",)

    def save_model(self, request, obj, form, change):
        password = form.cleaned_data.get('decryption_password')
        if password:
            obj.decryption_password = password
        super().save_model(request, obj, form, change)