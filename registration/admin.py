# registration/admin.py
import decimal
from django.utils.html import format_html
from django.urls import reverse, path
from django.contrib import admin
from django.http import HttpResponse
import csv
import openpyxl
from openpyxl.utils import get_column_letter

import gzip
import json
from django.utils import timezone

from .models import CandidateProfile
from results.models import CandidateAnswer


# -------------------------
# CSV exporter (candidate answers)
# -------------------------
def export_candidate_answers(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="selected_candidates_answers.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Army Number", "Candidate Name",
        "Paper Title", "Question ID", "Question Text", "Answer", "Submitted At"
    ])

    for candidate in queryset:
        answers = CandidateAnswer.objects.filter(candidate=candidate).select_related("candidate", "paper", "question")
        for ans in answers:
            writer.writerow([
                getattr(ans.candidate, "army_no", ""),
                ans.candidate.name if ans.candidate else "",
                getattr(ans.paper, "title", ""),
                getattr(ans.question, "id", ""),
                getattr(ans.question, "text", ""),
                getattr(ans, "answer", ""),
                getattr(ans, "submitted_at", ""),
            ])
    return response

export_candidate_answers.short_description = "Export selected candidates' answers to CSV"


# -------------------------
# Excel exporter (candidates)
# -------------------------
def export_candidates_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Candidates"

    columns = [
    "Army No", "Rank", "Name", "Trade", "DOB", "Father Name",
    "Date of Enrolment", "Aadhar Number",
    "Training Center", "District", "State",
    "Qualification", "NSQF Level",
    "Duration", "Credits",
    "Exam Center", "Shift",
    "Viva Marks", "Practical Marks",
    "Created At"
    ]

    for col_num, column_title in enumerate(columns, 1):
        ws.cell(row=1, column=col_num).value = column_title

    for row_num, candidate in enumerate(queryset, 2):
        data = [
            candidate.army_no,
            candidate.rank,
            candidate.name,
            candidate.trade,
            candidate.dob.strftime("%Y-%m-%d") if candidate.dob else "",
            candidate.father_name,
            candidate.doe.strftime("%Y-%m-%d") if candidate.doe else "",
            candidate.aadhar_number,
            candidate.training_center,
            candidate.district,
            candidate.state,
            candidate.qualification,
            candidate.nsqf_level,
            candidate.duration,
            candidate.credits,
            candidate.exam_center,
            str(candidate.shift) if candidate.shift else "",
            candidate.viva_marks if candidate.viva_marks is not None else "",
            candidate.practical_marks if candidate.practical_marks is not None else "",
            candidate.created_at.strftime("%Y-%m-%d %H:%M") if candidate.created_at else "",
        ]
        for col_num, cell_value in enumerate(data, 1):
            ws.cell(row=row_num, column=col_num, value=cell_value)

    for i in range(1, len(columns) + 1):
        ws.column_dimensions[get_column_letter(i)].width = 20

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="candidates.xlsx"'
    wb.save(response)
    return response

export_candidates_excel.short_description = "Export selected candidates to Excel"


# -------------------------
# DAT exporter (gzip JSON)
# -------------------------
def export_candidates_dat(modeladmin, request, queryset):
    export = {
        "meta": {
            "exported_at": timezone.now().isoformat(),
            "source": "ExamPortal",
            "version": "1.0",
            "count": queryset.count()
        },
        "candidates": []
    }

    for candidate in queryset.iterator():
        cand = {
            "id": candidate.pk,
            "army_no": candidate.army_no,
            "name": candidate.name,
            "user_username": candidate.user.username if candidate.user else "",
            "user_full_name": candidate.user.get_full_name() if candidate.user else "",
            "rank": candidate.rank,
            "trade": candidate.trade,
            "dob": candidate.dob.isoformat() if candidate.dob else None,
            "father_name": candidate.father_name,
            "doe": candidate.doe.isoformat() if candidate.doe else None,
            "aadhar_number": candidate.aadhar_number,
            "training_center": candidate.training_center,
            "district": candidate.district,
            "state": candidate.state,
            "qualification": candidate.qualification,
            "nsqf_level": candidate.nsqf_level,
            "credits": candidate.credits,
            "duration": candidate.duration,
            "exam_center": candidate.exam_center,
            "shift": str(candidate.shift) if candidate.shift else None,
            "viva_marks": candidate.viva_marks,
            "practical_marks": candidate.practical_marks,
            "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
            "photograph": candidate.photograph.url if candidate.photograph and hasattr(candidate.photograph, "url") else None,
            "answers": []
        }

        answers_qs = CandidateAnswer.objects.filter(candidate=candidate).select_related("paper", "question").order_by("paper_id", "question_id")
        for ans in answers_qs:
            ans_item = {
                "paper_id": getattr(ans.paper, "id", None),
                "paper_title": getattr(ans.paper, "title", None),
                "question_id": getattr(ans.question, "id", None),
                "question_text": getattr(ans.question, "text", None),
                "question_part": getattr(ans.question, "part", None),
                "answer": getattr(ans, "answer", None),
                "submitted_at": ans.submitted_at.isoformat() if ans.submitted_at else None,
            }
            cand["answers"].append(ans_item)

        export["candidates"].append(cand)

    def custom_serializer(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    json_bytes = json.dumps(export, ensure_ascii=False, default=custom_serializer).encode("utf-8")
    gz_bytes = gzip.compress(json_bytes)

    ts = timezone.now().strftime("%Y%m%d%H%M%S")
    filename = f"candidates_export_{ts}.dat"

    response = HttpResponse(gz_bytes, content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

export_candidates_dat.short_description = "Export selected candidates to binary (.dat gzip JSON)"


# -------------------------
# Admin Registration
# -------------------------
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("army_no", "name", "user", "rank", "trade", "viva_marks", "practical_marks", "shift", "created_at")
    actions = [export_candidate_answers, export_candidates_excel, export_candidates_dat]

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.username != "PO":
            readonly.extend(["viva_marks", "practical_marks"])
        return readonly

    def download_csv_link(self, obj):
        url = reverse("export_candidate_pdf", args=[obj.id])
        return format_html('<a class="button" href="{}">Download Answers PDF</a>', url)

    download_csv_link.short_description = "Export PDF"
    download_csv_link.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-all-dat/', self.admin_site.admin_view(self.export_all_dat_view), name='registration_candidateprofile_export_all_dat'),
        ]
        return custom_urls + urls

    def export_all_dat_view(self, request):
        qs = self.get_queryset(request)
        return export_candidates_dat(self, request, qs)
