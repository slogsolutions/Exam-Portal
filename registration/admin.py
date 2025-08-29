from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from django.http import HttpResponse
import csv
import openpyxl
from openpyxl.utils import get_column_letter

from .models import CandidateProfile
from results.models import CandidateAnswer


# ✅ Export candidate answers to CSV (already in your code)
def export_candidate_answers(modeladmin, request, queryset):
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
                ans.candidate.army_no,
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


# ✅ Export candidate details to Excel
def export_candidates_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Candidates"

    columns = [
        "Army No", "Rank", "Name", "Trade", "DOB", "Father Name",
        "Enrolment No", "Date of Enrolment", "Aadhar Number", "Unit",
        "Fmn (Bde)", "Fmn (Div)", "Fmn (Corps)", "Fmn (Comd)", "Training Centre",
        "District", "State",
        "Qualification", "Level of Qualification", "NSQF Level", "Skill", "QF",
        "Category", "Center", "Shift",
        "Created At"
    ]

    for col_num, column_title in enumerate(columns, 1):
        c = ws.cell(row=1, column=col_num)
        c.value = column_title

    for row_num, candidate in enumerate(queryset, 2):
        data = [
            candidate.army_no,
            candidate.rank,
            candidate.name,
            candidate.trade.name if candidate.trade else "",
            candidate.dob.strftime("%Y-%m-%d") if candidate.dob else "",
            candidate.father_name,
            candidate.enrolment_no,
            candidate.doe.strftime("%Y-%m-%d") if candidate.doe else "",
            candidate.aadhar_number,
            candidate.unit,
            candidate.fmn_bde,
            candidate.fmn_div,
            candidate.fmn_corps,
            candidate.fmn_comd,
            candidate.trg_centre,
            candidate.district,
            candidate.state,
            candidate.qualification.name if candidate.qualification else "",
            candidate.level_of_qualification.name if candidate.level_of_qualification else "",
            candidate.nsqf_level.name if candidate.nsqf_level else "",
            candidate.skill.name if candidate.skill else "",
            candidate.qf.name if candidate.qf else "",
            candidate.category.name if candidate.category else "",
            candidate.center.name if candidate.center else "",
            str(candidate.shift) if candidate.shift else "",
            candidate.created_at.strftime("%Y-%m-%d %H:%M"),
        ]
        for col_num, cell_value in enumerate(data, 1):
            ws.cell(row=row_num, column=col_num, value=cell_value)

    for i, column in enumerate(columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = 20

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="candidates.xlsx"'
    wb.save(response)
    return response

export_candidates_excel.short_description = "Export selected candidates to Excel"


# ✅ Admin Registration
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("army_no", "name", "user", "category", "viva_marks", "practical_marks", "download_csv_link")
    actions = [export_candidate_answers, export_candidates_excel]

    def get_readonly_fields(self, request, obj=None):
        """
        Allow only the user with username 'Examiner' to edit viva_marks and practical_marks.
        """
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.username != "PO":
            readonly.extend(["viva_marks", "practical_marks"])
        return readonly

    def download_csv_link(self, obj):
        url = reverse("export_candidate_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}">Download Answers pdf</a>', url)

    download_csv_link.short_description = "Export PDF"
    download_csv_link.allow_tags = True

