from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import CandidateProfile
from .forms import CandidateRegistrationForm

@login_required
def candidate_dashboard(request):
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


def exam_interface(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    if not candidate_profile.can_start_exam:
        return render(request, "registration/exam_not_started.html", {"message": "You cannot start the exam yet."})

    return render(request, "registration/exam_interface.html", {"candidate": candidate_profile})