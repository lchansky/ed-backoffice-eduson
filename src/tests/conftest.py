from django.contrib.auth.models import User
import pytest


@pytest.fixture
@pytest.mark.django_db
def user():

    user = User.objects.create_user(
        username='user',
        email='jlennon@beatles.com',
        password='password',
    )
    return user
