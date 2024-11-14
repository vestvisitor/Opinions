from crispy_forms.layout import Submit, Layout, HTML, Field, Div, BaseInput
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django.forms import ModelForm


class UserSigninForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="")

    class Meta:
        model = User
        fields = ["username", "password"]
        help_texts = {
            'username': None,
            'password': None,
        }
        css_class = {
            'username': "form-control",
            'password': "form-control",
        }
        labels = {
            'username': "",
            'password': "",
        }

    helper = FormHelper()
    helper.layout =Layout(
        HTML("""<label for="floatingInput">Username</label>"""),
        Field("username", wrapper_class="form-floating", id="floatingInput"),
        HTML("""<label for="floatingPassword">Password</label>"""),
        Field("password", wrapper_class="form-floating", id="floatingPassword"),
        HTML("""{% for message in messages %}

                  <div class="alert alert-danger" role="alert">
                      <a class="close" href="#" data-dismiss="alert">×</a>
                      {{ message }}
                  </div>
            
                {% endfor %}"""),
        HTML("""<p class="text-center">Don't have an account? <a href="{% url 'users:signup' %}">Sign up</a>""")
    )
    helper.add_input(Submit('submit', value='Sign in', css_class='btn btn-primary w-100 py-2'))
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy("users:signin")


class UserSignupForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="")

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        help_texts = {
            'username': None,
            'email': None,
        }
        labels = {
            'username': "",
            'email': "",
        }

    helper = FormHelper()
    helper.layout = Layout(
        HTML("""<label for="floatingUsername">Username</label>"""),
        Field("username", wrapper_class="form-floating", id="floatingUsername"),
        HTML("""<label for="floatingEmail">Email</label>"""),
        Field("email", wrapper_class="form-floating", id="floatingEmail", required=True),
        HTML("""<label for="floatingPassword">Password</label>"""),
        Field("password", wrapper_class="form-floating", id="floatingPassword"),
        HTML("""<label for="floatingPassword1">Confrimation password</label>"""),
        Field("password_confirm", wrapper_class="form-floating", id="floatingPassword1"),
        HTML("""{% for message in messages %}

                      <div class="alert alert-danger" role="alert">
                          <a class="close" href="#" data-dismiss="alert">×</a>
                          {{ message }}
                      </div>

                    {% endfor %}"""),
        HTML("""<p class="text-center">Already have an account? <a href="{% url 'users:signin' %}">Sign in</a></p>""")
    )

    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-primary w-100 py-2'))
    helper.form_method = 'POST'
    helper.form_action = reverse_lazy("users:signup")
