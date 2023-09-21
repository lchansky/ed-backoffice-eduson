import pytest
from django.contrib.auth.models import User, Permission

from certificates.models import Course


@pytest.fixture
@pytest.mark.django_db
def course():
    return Course.objects.create(name='Python', hours=100)


@pytest.fixture
@pytest.mark.django_db
def user_with_certificates_permissions():

    user = User.objects.create_user(
        username='user',
        email='mail@email.com',
        password='password',
    )

    permissions = Permission.objects.filter(codename__endswith='certificate')
    for permission in permissions:
        user.user_permissions.add(permission)
    user.save()
    return user


@pytest.fixture
@pytest.mark.django_db
def user_with_courses_permissions():

    user = User.objects.create_user(
        username='user',
        email='mail@email.com',
        password='password',
    )

    permissions = Permission.objects.filter(codename__endswith='course')
    for permission in permissions:
        user.user_permissions.add(permission)
    user.save()
    return user
