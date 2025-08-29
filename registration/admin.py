from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from .models import CandidateProfile
from results.models import CandidateAnswer


def export_candidate_answers(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="selected_candidates_answers.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Army Number", "Candidate Name", "Category",
        "Paper Title", "Question ID", "Question Text", "Answer", "Submitted At"
    ])

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


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("army_no", "user", "category", "can_start_exam", "download_csv_link")
    actions = [export_candidate_answers]

    def download_csv_link(self, obj):
        url = reverse("export_candidate_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}">Download Answers pdf</a>', url)
    download_csv_link.short_description = "Export PDF"
    download_csv_link.allow_tags = True
