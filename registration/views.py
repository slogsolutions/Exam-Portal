from django.shortcuts import render, redirect
from .forms import CandidateRegistrationForm

def register_candidate(request):
    if request.method == "POST":
        
        print("Form is valid")
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print("Form is valid and saved")
            return redirect("registration_success")  # Define this URL/view
        else:
            print("error")
    else:
        print("invalid")
        form = CandidateRegistrationForm()
    return render(request, "registration/register_candidate.html", {"form": form})
