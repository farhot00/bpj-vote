from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from turnstile.fields import TurnstileField

from .models import Candidate, Vote, Voter

class VoteForm(forms.Form):
    candidates = forms.ModelMultipleChoiceField(
        queryset=Candidate.objects.none().order_by("id"),  # Will be set dynamically in the view
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'candidate-checkbox'}),
        label="بین ۱ تا ۵ کاندیدا انتخاب کنید."
    )
    turnstile = TurnstileField()

    def __init__(self, *args, **kwargs):
        voter = kwargs.pop('voter', None)
        super(VoteForm, self).__init__(*args, **kwargs)

        # Filter candidates by the voter's scientific association
        if voter:
            self.fields['candidates'].queryset = Candidate.objects.filter(
                scientific_association=voter.scientific_association).order_by("id")
        else:
            raise forms.ValidationError("voter object must be passed to this form.")

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Vote'))

    def clean_candidates(self):
        cleaned_data = super().clean()
        candidates = cleaned_data['candidates']
        if not candidates:
            raise forms.ValidationError("شما باید حداقل ۱ کاندیدا انتخاب کنید.")
        if len(candidates) > 5:
            raise forms.ValidationError("شما میتوانید حداکثر ۵ کاندیدا انتخاب کنید.")
        if len(candidates) != len(set(candidates)):
            raise forms.ValidationError("شما نمیتوانید به یک کاندیدا رای تکراری بدهید.")
        return candidates