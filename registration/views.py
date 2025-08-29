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

# views.py (relevant part)
# from django.shortcuts import render, redirect
from django.contrib import messages
# from .forms import CandidateRegistrationForm

def register_candidate(request):
    if request.method == "POST":
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save()   # form creates User and CandidateProfile correctly
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")  # or redirect to whichever page you prefer
        else:
            # Optional: log or print errors to console for debugging
            print("Registration form invalid:", form.errors)
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
            if key.startswith("question_"):
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
import tempfile
from django.http import FileResponse, Http404
from results.models import CandidateAnswer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.pdfencrypt import StandardEncryption


def export_answers_pdf(request, candidate_id):
    try:
        answers = CandidateAnswer.objects.filter(candidate_id=candidate_id).select_related(
            "candidate", "paper", "question"
        )

        if not answers.exists():
            raise Http404("No answers found for this candidate.")

        # Candidate details
        candidate = answers[0].candidate
        army_no = getattr(candidate, "army_no", candidate.user.username)
        candidate_name = candidate.user.get_full_name()

        filename = f"{army_no}_answers.pdf"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        # PDF password protection (password = Army No)
        password = army_no
        from reportlab.lib.pdfencrypt import StandardEncryption
        enc = StandardEncryption(
            userPassword=password,
            ownerPassword="sarthak",
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0
        )

        # Create PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch

        c = canvas.Canvas(tmp_path, pagesize=A4, encrypt=enc)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Candidate Answers Export")

        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Army No: {army_no}")
        c.drawString(1 * inch, height - 1.8 * inch, f"Name: {candidate_name}")
        c.drawString(1 * inch, height - 2.1 * inch, f"Category: {candidate.category}")
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
