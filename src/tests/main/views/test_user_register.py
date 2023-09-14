import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from main.models import Invitation

User = get_user_model()


@pytest.mark.django_db
def test_invitation_create():
    invitation = Invitation.objects.create()
    assert invitation.invite_code


@pytest.mark.django_db
def test_cant_register_without_invitation():
    c = Client()

    response = c.post(
        reverse('register'),
        data={
            'username': 'user12345',
            'password1': 'passWORD123jfdslfsd',
            'password2': 'passWORD123jfdslfsd',
        },
    )

    assert response.status_code == 200
    assert User.objects.count() == 0
    form = response.context['form']
    assert hasattr(form, 'errors')
    assert form.errors['invitation_code'][0] == 'Обязательное поле.'


@pytest.mark.django_db
def test_cant_register_with_wrong_invitation():
    c = Client()

    response = c.post(
        reverse('register'),
        data={
            'username': 'user12345',
            'password1': 'passWORD123jfdslfsd',
            'password2': 'passWORD123jfdslfsd',
            'invitation_code': 'not_existing_code',
        },
    )

    assert response.status_code == 200
    assert User.objects.count() == 0
    form = response.context['form']
    assert hasattr(form, 'errors')
    assert (
        form.errors['invitation_code'][0] ==
        'Инвайт-код недействителен или уже использован. Обратитесь к администрации.'
    )


@pytest.mark.django_db
def test_cant_register_with_used_invitation_code():
    invitation = Invitation.objects.create()
    user1 = User.objects.create(username='user1', password='password')
    invitation.use(user1)

    c = Client()
    response = c.post(
        reverse('register'),
        data={
            'username': 'user12345',
            'password1': 'passWORD123jfdslfsd',
            'password2': 'passWORD123jfdslfsd',
            'invitation_code': 'not_existing_code',
        },
    )

    assert invitation.is_used
    assert response.status_code == 200
    assert User.objects.count() == 1
    with pytest.raises(User.DoesNotExist):
        User.objects.get(username='user12345')

    form = response.context['form']
    assert hasattr(form, 'errors')
    assert (
            form.errors['invitation_code'][0] ==
            'Инвайт-код недействителен или уже использован. Обратитесь к администрации.'
    )


@pytest.mark.django_db
def test_successfully_register():
    c = Client()
    permissions = Permission.objects.filter(codename__in=['add_promocode', 'change_promocode', 'view_promocode'])
    invitation = Invitation.objects.create()
    invitation.permissions.set(permissions)
    invitation.save()

    response = c.post(
        reverse('register'),
        data={
            'username': 'user12345',
            'password1': 'passWORD123jfdslfsd',
            'password2': 'passWORD123jfdslfsd',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'invitation_code': str(invitation.invite_code),
        },
    )
    invitation.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse('login')

    user = User.objects.first()
    assert User.objects.count() == 1
    assert user.username == 'user12345'
    assert user.first_name == 'Иван'
    assert user.last_name == 'Иванов'
    assert user.has_perm('promocodes.add_promocode')
    assert user.has_perm('promocodes.change_promocode')
    assert user.has_perm('promocodes.view_promocode')

    assert invitation.is_used
    assert invitation.used_at
    assert invitation.used_by == user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field",
    ['username', 'password1', 'password2', 'first_name', 'last_name', 'invitation_code'],
    ids=['username', 'password1', 'password2', 'first_name', 'last_name', 'invitation_code'],
)
def test_cant_register_without_any_field(field):
    c = Client()
    permissions = Permission.objects.filter(codename__in=['add_promocode', 'change_promocode', 'view_promocode'])
    invitation = Invitation.objects.create()
    invitation.permissions.set(permissions)
    invitation.save()

    data = {
        'username': 'user12345',
        'password1': 'passWORD123jfdslfsd',
        'password2': 'passWORD123jfdslfsd',
        'first_name': 'Иван',
        'last_name': 'Иванов',
        'invitation_code': str(invitation.invite_code),
    }
    data.pop(field)

    response = c.post(
        reverse('register'),
        data=data,
    )
    invitation.refresh_from_db()

    assert response.status_code == 200
    assert User.objects.count() == 0
    form = response.context['form']
    assert hasattr(form, 'errors')

