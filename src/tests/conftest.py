from django.contrib.auth.models import User
import pytest


@pytest.fixture
@pytest.mark.django_db
def user():

    user = User.objects.create_user(
        username='john',
        email='jlennon@beatles.com',
        password='glass onion',
    )
    return user
