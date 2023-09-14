import uuid

from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import TextInput, CharField, PasswordInput
from django.utils.translation import gettext_lazy

from main.models import Invitation


User = get_user_model()


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


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "invitation_code", "first_name", "last_name")

    username = CharField(
        label='Имя пользователя',
        widget=TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        ),
    )
    password1 = CharField(
        label='Пароль',
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
            },
        ),
    )
    password2 = CharField(
        label='Повторите пароль',
        widget=PasswordInput(
            attrs={
                'class': 'form-control',
            },
        ),
    )
    invitation_code = CharField(
        label='Инвайт код',
        widget=TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    first_name = CharField(
        label='Имя',
        widget=TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )
    last_name = CharField(
        label='Фамилия',
        widget=TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    def clean_invitation_code(self):
        invitation_code = self.cleaned_data['invitation_code']
        try:
            uuid_code = uuid.UUID(invitation_code)
        except Exception as exc:
            raise ValidationError("Инвайт-код недействителен или уже использован. Обратитесь к администрации.")
        try:
            Invitation.objects.get(invite_code=uuid_code, is_used=False)
        except (Invitation.DoesNotExist, ValidationError):
            raise ValidationError("Инвайт-код недействителен или уже использован. Обратитесь к администрации.")
        return invitation_code

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            invitation = Invitation.objects.get(invite_code=self.cleaned_data['invitation_code'])
            invitation.use(user)
        return user


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
