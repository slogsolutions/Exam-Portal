from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import CandidateProfile
from .forms import CandidateRegistrationForm

@login_required
def candidate_dashboard(request):
    print(request.user)
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    exams_scheduled = []
    upcoming_exams = []
    completed_exams = []
    results = []

    return render(request, "registration/dashboard.html", {
        "candidate": candidate_profile,
        "exams_scheduled": exams_scheduled,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "results": results,
    })

def register_candidate(request):
    if request.method == "POST":
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user   # ✅ link logged-in user
            candidate.save()
            return redirect("login")
    else:
        form = CandidateRegistrationForm()
    return render(request, "registration/register_candidate.html", {"form": form})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from questions.models import QuestionPaper, Question
from results.models import CandidateAnswer
from registration.models import CandidateProfile

@login_required
def exam_interface(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)

    # check if candidate is allowed
    if not candidate_profile.can_start_exam:
        return render(request, "registration/exam_not_started.html", {
            "message": "You cannot start the exam yet."
        })

    # load question papers
    category = candidate_profile.category
    part_a = QuestionPaper.objects.filter(category=category, is_common=False).first()
    part_b = QuestionPaper.objects.filter(category=category,is_common=True).first()

    # save answers
    if request.method == "POST":
        paper_id = request.POST.get("paper_id")
        paper = QuestionPaper.objects.get(id=paper_id)

        for key, value in request.POST.items():
            if key.startswith("question_"):  # e.g. question_5
                qid = key.split("_")[1]
                question = Question.objects.get(id=qid)
                CandidateAnswer.objects.update_or_create(
                    candidate=candidate_profile,
                    paper=paper,
                    question=question,
                    defaults={"answer": value}
                )
        return redirect("exam_interface")  # reload after save

    return render(request, "registration/exam_interface.html", {
        "candidate": candidate_profile,
        "part_a": part_a,
        "part_b": part_b,
    })



import os
import json
import tempfile
from django.http import FileResponse, Http404
from results.models import CandidateAnswer

def export_candidate_json(request, candidate_id):
    try:
        answers = CandidateAnswer.objects.filter(candidate_id=candidate_id).select_related(
            "candidate", "paper", "question"
        )

        if not answers.exists():
            raise Http404("No answers found for this candidate.")

        # Prepare JSON data
        data = []
        for ans in answers:
            data.append({
                "army_number": getattr(ans.candidate, "army_no", ans.candidate.user.username),
                "candidate_name": getattr(ans.candidate, "name", ans.candidate.user.get_full_name()),
                "category": str(ans.candidate.category),
                "paper_title": ans.paper.title,
                "question_id": ans.question.id,
                "question_text": ans.question.text,
                "answer": ans.answer,
                "submitted_at": ans.submitted_at.isoformat(),
            })

        json_data = json.dumps(data, indent=4).encode("utf-8")

        # File name
        army_no = getattr(answers[0].candidate, "army_no", answers[0].candidate.user.username)
        filename = f"{army_no}_answers.json"

        # Save to temp file
        tmp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(tmp_path, "wb") as f:
            f.write(json_data)

        # Make file read-only
        os.chmod(tmp_path, 0o444)  # read-only for everyone

        # Return file as download
        response = FileResponse(open(tmp_path, "rb"), as_attachment=True, filename=filename)
        return response

    except Exception as e:
        raise Http404(f"Error exporting candidate answers: {e}")

