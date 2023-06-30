from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, TextInput, DateInput, CharField, PasswordInput, NumberInput, Select

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

