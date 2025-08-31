from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import CandidateProfile
from reference.models import Trade
from .forms import CandidateRegistrationForm
from django.contrib import messages
from questions.models import QuestionPaper, Question
from results.models import CandidateAnswer
from django.http import FileResponse, Http404
import os, tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.pdfencrypt import StandardEncryption


@login_required
def candidate_dashboard(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    exams_scheduled, upcoming_exams, completed_exams, results = [], [], [], []
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
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
        else:
            print("Registration form invalid:", form.errors)
    else:
        form = CandidateRegistrationForm()
    return render(request, "registration/register_candidate.html", {"form": form})


@login_required
def exam_interface(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)

    if not candidate_profile.can_start_exam:
        return render(request, "registration/exam_not_started.html", {
            "message": "You cannot start the exam yet."
        })

    trade_obj = None
    if candidate_profile.trade:
        print(candidate_profile.trade)
        trade_obj = get_object_or_404(Trade, name=candidate_profile.trade)
    part_a = QuestionPaper.objects.filter(trade=trade_obj, is_common=False).first()
    part_b = QuestionPaper.objects.filter(trade=trade_obj, is_common=True).first()
    current_paper = part_a or part_b
    duration_seconds = int(current_paper.duration.total_seconds()) if current_paper and current_paper.duration else 0
    if request.method == "POST":
        paper_id = request.POST.get("paper_id")
        paper = QuestionPaper.objects.get(id=paper_id)
        for key, value in request.POST.items():
            if key.startswith("question_"):
                qid = key.split("_")[1]
                question = Question.objects.get(id=qid)
                CandidateAnswer.objects.update_or_create(
                    candidate=candidate_profile,
                    paper=paper,
                    question=question,
                    defaults={"answer": value}
                )
        # redirect to success page instead of reloading exam
        return redirect("exam_success")

    return render(request, "registration/exam_interface.html", {
        "candidate": candidate_profile,
        "part_a": part_a,
        "part_b": part_b,
        "duration_seconds": duration_seconds,
    })


@login_required
def exam_success(request):
    return render(request, "registration/exam_success.html")


def export_answers_pdf(request, candidate_id):
    try:
        answers = CandidateAnswer.objects.filter(candidate_id=candidate_id).select_related(
            "candidate", "paper", "question"
        )
        if not answers.exists():
            raise Http404("No answers found for this candidate.")

        candidate = answers[0].candidate
        army_no = getattr(candidate, "army_no", candidate.user.username)
        candidate_name = candidate.user.get_full_name()

        filename = f"{army_no}_answers.pdf"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        enc = StandardEncryption(
            userPassword=army_no,
            ownerPassword="sarthak",
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0
        )

        c = canvas.Canvas(tmp_path, pagesize=A4, encrypt=enc)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Candidate Answers Export")
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Army No: {army_no}")
        c.drawString(1 * inch, height - 1.8 * inch, f"Name: {candidate_name}")
        c.drawString(1 * inch, height - 2.1 * inch, f"Trade: {candidate.trade}")
        c.drawString(1 * inch, height - 2.4 * inch, f"Paper: {answers[0].paper.title}")

        y = height - 3 * inch
        c.setFont("Helvetica", 11)
        for idx, ans in enumerate(answers, start=1):
            question_text = (ans.question.text[:80] + "...") if len(ans.question.text) > 80 else ans.question.text
            c.drawString(1 * inch, y, f"Q{idx}: {question_text}")
            y -= 0.3 * inch
            c.drawString(1.2 * inch, y, f"Answer: {ans.answer}")
            y -= 0.5 * inch
            if y < 1.5 * inch:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 1 * inch

        c.save()
        return FileResponse(open(tmp_path, "rb"), as_attachment=True, filename=filename)

    except Exception as e:
        raise Http404(f"Error exporting candidate answers: {e}")
