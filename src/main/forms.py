from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.forms import TextInput, CharField, PasswordInput
from django.utils.translation import gettext_lazy



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
