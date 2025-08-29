from django.contrib import admin
from .models import Question, QuestionPaper, PaperQuestion, QuestionUpload
import openpyxl
import docx


class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 1
    autocomplete_fields = ["question"]  # 🔥 searchable dropdown for questions


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "part", "marks", "level", "skill", "category", "is_active")
    list_filter = ("part", "level", "skill", "category", "is_active")
    search_fields = ("text",)


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ("title", "upload", "is_common", "level", "skill", "category", "active_from", "active_to")
    list_filter = ("is_common", "level", "skill", "category")
    inlines = [PaperQuestionInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 🔥 If a file is linked, auto-attach its questions to this paper
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
    list_display = ("file", "uploaded_at")
    search_fields = ("file",)

    def save_model(self, request, obj, form, change):
        """Handle file upload and trigger import"""
        super().save_model(request, obj, form, change)

        if obj.file.name.endswith(".xlsx"):
            self.import_from_excel(obj.file.path)
        elif obj.file.name.endswith(".docx"):
            self.import_from_word(obj.file.path)

    # -----------------------------
    # ✅ Import from Excel
    # -----------------------------
    def import_from_excel(self, filepath):
        wb = openpyxl.load_workbook(filepath)
        sheet = wb.active

        for row in sheet.iter_rows(min_row=2, values_only=True):  # skip header
            part, question_text, opt_a, opt_b, opt_c, opt_d = row

            if not part or not question_text:
                continue  # skip empty rows

            if part in ["A", "B", "C"]:  # Objective
                Question.objects.create(
                    part=part,
                    text=question_text,
                    options={"choices": [opt_a, opt_b, opt_c, opt_d]},
                )
            if part in ["F"]:  # TRUE/FALSE
                Question.objects.create(
                    part=part,
                    text=question_text,
                    options={"choices": [opt_a, opt_b]},
                )
            if part in ["D"]:  # Descriptive
                Question.objects.create(
                    part=part,
                    text=question_text,
                )
            if part in ["E"]:  # Descriptive
                Question.objects.create(
                    part=part,
                    text=question_text,
                )
            

    # -----------------------------
    # ✅ Import from Word
    # -----------------------------
    def import_from_word(self, filepath):
        doc = docx.Document(filepath)
        question_text, options, correct, marks, part, desc_answer = None, [], None, 1, None, None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            if text.startswith("Q"):  # New Question
                if question_text:  # Save previous
                    self._save_question(part, question_text, options, correct, desc_answer, marks)

                # Reset
                question_text, options, correct, marks, part, desc_answer = text, [], None, 1, None, None

            elif text.startswith("Part:"):
                part = text.split(":", 1)[1].strip().upper()

            elif text.startswith(("A)", "B)", "C)", "D)")):
                options.append(text[2:].strip())

            elif text.startswith("Answer:"):
                ans = text.split(":", 1)[1].strip()
                if part in ["A", "B", "C"]:
                    correct = ans
                else:
                    desc_answer = ans

            elif text.startswith("Marks:"):
                try:
                    marks = int(text.split(":", 1)[1].strip())
                except:
                    marks = 1

        # Save last question
        if question_text:
            self._save_question(part, question_text, options, correct, desc_answer, marks)

    # -----------------------------
    # ✅ Helper
    # -----------------------------
    def _save_question(self, part, question_text, options, correct, desc_answer, marks):
        if not part:
            return  # avoid NULL part

        if part in ["A", "B", "C"]:
            Question.objects.create(
                part=part,
                text=question_text,
                options={"choices": options},
                correct_answer=correct,
                marks=marks,
            )
        elif part in ["D", "E"]:
            Question.objects.create(
                part=part,
                text=question_text,
                correct_answer=desc_answer,
                marks=marks,
            )



import csv
from django.http import HttpResponse
from django.contrib import admin
from registration.models import CandidateProfile
from results.models import CandidateAnswer  # import your answers model

def export_candidate_answers(modeladmin, request, queryset):
    """
    Admin action to export selected candidates' answers as CSV.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="selected_candidates_answers.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Army Number", "Candidate Name", "Category",
        "Paper Title", "Question ID", "Question Text", "Answer", "Submitted At"
    ])

    # loop through selected candidates
    for candidate in queryset:
        answers = CandidateAnswer.objects.filter(candidate=candidate).select_related("candidate", "paper", "question")
        for ans in answers:
            writer.writerow([
                ans.candidate.army_number,
                ans.candidate.user.get_full_name(),
                ans.candidate.category,
                ans.paper.title,
                ans.question.id,
                ans.question.text,
                ans.answer,
                ans.submitted_at,
            ])

    return response

export_candidate_answers.short_description = "Export selected candidates' answers to CSV"


# @admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("army_number", "user", "category", "can_start_exam")
    actions = [export_candidate_answers]  # ✅ Add the action here
