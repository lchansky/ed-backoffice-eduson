from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.forms import ModelForm, TextInput, DateInput, CharField, PasswordInput, NumberInput, Select
from django.utils.translation import gettext_lazy

from .models import Certificate, Course


class CertificateCreateForm(ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_fio': TextInput(attrs={'class': 'form-control'}),
            'course': Select(attrs={'class': 'form-select'}),
        }


class CertificateEditForm(ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'student_fio': TextInput(attrs={'class': 'form-control'}),
            'course': Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['date'] = self.instance.date.isoformat()


class CourseCreateForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'hours': NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }


class CourseEditForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'hours': NumberInput(attrs={'class': 'form-control'}),
        }


class UserLoginForm(AuthenticationForm):
    username = CharField(
        label='Имя пользователя',
        widget=TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        ),
    )
    password = CharField(
        label='Пароль',
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'current-password'
            },
        ),
    )


class UserSettingsForm(PasswordChangeForm):
    old_password = CharField(
        label=gettext_lazy("Old password"),
        strip=False,
        widget=PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True, "class": "form-control"}
        ),
    )
    new_password1 = CharField(
        label=gettext_lazy("New password"),
        widget=PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = CharField(
        label=gettext_lazy("New password confirmation"),
        strip=False,
        widget=PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
    )
