from django import forms
from .models import DigitalAddictionAssessment


class DigitalAddictionForm(forms.ModelForm):
    class Meta:
        model = DigitalAddictionAssessment
        exclude = ["student", "predicted_risk", "created_at"]
