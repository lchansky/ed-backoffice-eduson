from django.contrib.auth.models import User, Permission
import pytest


@pytest.fixture
@pytest.mark.django_db
def user_with_promocodes_permissions():

    user = User.objects.create_user(
        username='user',
        email='mail@email.com',
        password='password',
    )

    permissions = Permission.objects.filter(codename__endswith='promocode')
    for permission in permissions:
        user.user_permissions.add(permission)
    user.save()
    return user
