from django import forms
from django.contrib.auth import get_user_model
from .models import CandidateProfile

User = get_user_model()

class CandidateRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

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

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"]
        )
        candidate = CandidateProfile.objects.create(
            user=user,
            army_no=self.cleaned_data["army_no"],
            rank=self.cleaned_data["rank"],
            name=self.cleaned_data["name"],
            trade=self.cleaned_data["trade"],
            dob=self.cleaned_data["dob"],
            father_name=self.cleaned_data["father_name"],
            enrolment_no=self.cleaned_data["enrolment_no"],
            doe=self.cleaned_data["doe"],
            aadhar_number=self.cleaned_data["aadhar_number"],
            unit=self.cleaned_data["unit"],
            fmn_bde=self.cleaned_data["fmn_bde"],
            fmn_div=self.cleaned_data["fmn_div"],
            fmn_corps=self.cleaned_data["fmn_corps"],
            fmn_comd=self.cleaned_data["fmn_comd"],
            trg_centre=self.cleaned_data["trg_centre"],
            district=self.cleaned_data["district"],
            state=self.cleaned_data["state"],
            qualification=self.cleaned_data["qualification"],
            level_of_qualification=self.cleaned_data["level_of_qualification"],
            nsqf_level=self.cleaned_data["nsqf_level"],
            skill=self.cleaned_data["skill"],
            qf=self.cleaned_data["qf"],
            category=self.cleaned_data["category"],
            center=self.cleaned_data["center"],
            shift=self.cleaned_data["shift"],
            photograph=self.cleaned_data.get("photograph"),
        )
        return candidate
