from enum import unique

from annotated_types.test_cases import cases
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse_lazy
from .models import Case, Opinion, CaseOpinion
from crispy_forms.helper import FormHelper
from django.forms import ModelForm


class CaseCreateForm(ModelForm):

    class Meta:
        model = Case
        fields = ["case_title", "tags", "case_text", "is_anonymous"]

    helper = FormHelper()
    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-success'))
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy("cases:publish")


class CaseEditForm(ModelForm):

    class Meta:
        model = Case
        fields = ["case_title", "tags", "case_text", "is_anonymous"]

    helper = FormHelper()
    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-success'))
    helper.form_method = 'POST'


class OpinionCreateForm(ModelForm):

    caseid = forms.IntegerField(initial=0)
    caseid.widget = caseid.hidden_widget()

    def __init__(self, *args, **kwargs):
        try:
            self.caseid = kwargs.pop("case_id")
            super(OpinionCreateForm, self).__init__(*args, **kwargs)
            self.fields["caseid"].initial = self.caseid
        except KeyError:
            pass

    class Meta:
        model = Opinion
        fields = ["opinion_text", "is_anonymous"]

    helper = FormHelper()

    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-success'))
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy("cases:opinion", kwargs={'case_id': caseid.initial})
