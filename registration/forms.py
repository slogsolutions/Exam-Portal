# forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import CandidateProfile

User = get_user_model()

class CandidateRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = CandidateProfile
        fields = [
            "army_no", "rank", "name", "trade", "dob", "father_name",
            "enrolment_no", "doe", "aadhar_number", "unit",
            "fmn_bde", "fmn_div", "fmn_corps", "fmn_comd",
            "trg_centre", "district", "state", "qualification",
            "level_of_qualification", "nsqf_level", "skill", "qf",
            "photograph", "category", "center", "shift"
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "doe": forms.DateInput(attrs={"type": "date", "class": "form-control"})
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self, commit=True):
        # Create the User first
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # create_user will hash the password
        user = User.objects.create_user(username=username, password=password)

        # Create CandidateProfile instance but don't save to DB yet
        candidate = super().save(commit=False)
        candidate.user = user

        if commit:
            candidate.save()  # will also save file fields (photograph) provided request.FILES passed into form
        return candidate