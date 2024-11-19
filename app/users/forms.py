from crispy_forms.layout import Submit, Layout, HTML, Field, Div, BaseInput
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError


class UserSigninForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="")

    class Meta:
        model = User
        fields = ["username", "password"]
        help_texts = {
            'username': None,
            'password': None,
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


class UserSignupForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'email', 'password1', 'password2']:
            self.fields[field_name].help_text = None
            self.fields[field_name].label = ""

    def validate_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and self._meta.model.objects.filter(email__iexact=email).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "email": self.instance.unique_error_message(
                            self._meta.model, ["email"]
                        )
                    }
                )
            )
        else:
            return email

    helper = FormHelper()
    helper.layout = Layout(
        HTML("""<label for="floatingUsername">Username</label>"""),
        Field("username", wrapper_class="form-floating", id="floatingUsername"),
        HTML("""<label for="floatingEmail">Email</label>"""),
        Field("email", wrapper_class="form-floating", id="floatingEmail", required=True),
        HTML("""<label for="floatingPassword">Password</label>"""),
        Field("password1", wrapper_class="form-floating", id="floatingPassword"),
        HTML("""<label for="floatingPassword1">Confrimation password</label>"""),
        Field("password2", wrapper_class="form-floating", id="floatingPassword1"),
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


class UserEditForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User
        fields = ('username','email')
        help_texts = {
            'username': None,
            'email': None,
        }
        labels = {
            'username': "",
            'email': "",
        }

    def validate_email(self):
        email = self.data.get("email")
        if (
                email
                and self._meta.model.objects.filter(email__iexact=email).exists()
        ):
            self._update_errors(
                ValidationError(
                    {
                        "email": self.instance.unique_error_message(
                            self._meta.model, ["email"]
                        )
                    }
                )
            )
        else:
            return email

    helper = FormHelper()
    helper.layout = Layout(
        Div(HTML("""<a href="{% url 'avatar:change' %}">Change your avatar</a>""")),
        HTML("""<label for="floatingUsername">Username</label>"""),
        Field("username", wrapper_class="form-floating", id="floatingUsername"),
        HTML("""<label for="floatingEmail">Email</label>"""),
        Field("email", wrapper_class="form-floating", id="floatingEmail", required=True),
        HTML("""<a href="{% url 'users:edit_password' %}">Change password</a>"""),
        HTML("""{% for message in messages %}

                          <div class="alert alert-danger" role="alert">
                              <a class="close" href="#" data-dismiss="alert">×</a>
                              {{ message }}
                          </div>

                        {% endfor %}"""),
    )

    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-primary w-100 py-2'))
    helper.form_method = 'POST'


class UserChangePasswordForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].help_text = None
            self.fields[field_name].label = ""

    helper = FormHelper()
    helper.layout = Layout(
        HTML("""<label for="floatingOldPassword">Old password</label>"""),
        Field("old_password", wrapper_class="form-floating", id="floatingOldPassword"),
        HTML("""<label for="floatingNewPassword">New password</label>"""),
        Field("new_password1", wrapper_class="form-floating", id="floatingNewPassword", required=True),
        HTML("""<label for="floatingConfirmation">New confirmation password</label>"""),
        Field("new_password2", wrapper_class="form-floating", id="floatingConfirmation"),
        HTML("""{% for message in messages %}

                              <div class="alert alert-danger" role="alert">
                                  <a class="close" href="#" data-dismiss="alert">×</a>
                                  {{ message }}
                              </div>

                            {% endfor %}"""),
    )

    helper.add_input(Submit('submit', value='Submit', css_class='btn btn-primary w-100 py-2'))
    helper.form_method = 'POST'
