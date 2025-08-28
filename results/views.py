import csv
from django.http import HttpResponse
from .models import CandidateAnswer

def export_answers_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="candidate_answers.csv"'

    writer = csv.writer(response)
    # Header row
    writer.writerow([
        "Army Number",
        "Candidate Name",
        "Category",
        "Paper Title",
        "Question ID",
        "Question Text",
        "Answer",
        "Submitted At"
    ])

    for ans in CandidateAnswer.objects.select_related("candidate", "paper", "question"):
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
