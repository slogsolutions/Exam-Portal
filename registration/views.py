from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import CandidateProfile
# assuming you have Exam / Result models, otherwise dummy placeholders
# from exams.models import Exam, Result  

@login_required
def candidate_dashboard(request):
    # fetch candidate profile using logged-in user
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)

    # TODO: replace below placeholders with actual querysets from Exam / Result models
    exams_scheduled = []   # Example: Exam.objects.filter(candidate=candidate_profile, status="scheduled")
    upcoming_exams = []    # Example: Exam.objects.filter(candidate=candidate_profile, status="upcoming")
    completed_exams = []   # Example: Exam.objects.filter(candidate=candidate_profile, status="completed")
    results = []           # Example: Result.objects.filter(candidate=candidate_profile)

    return render(request, "registration/dashboard.html", {
        "candidate": candidate_profile,
        "exams_scheduled": exams_scheduled,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "results": results,
    })
