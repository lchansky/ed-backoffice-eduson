import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from certificates.models import Course
from tests.conftest import user


@pytest.mark.django_db
def test_create_course_with_permission(user):
    c = Client()
    permission = Permission.objects.get(codename='add_course')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.add_course')

    assert c.login(username='user', password='password')

    course_create_endpoint = reverse("course_create")
    response = c.post(
        course_create_endpoint,
        data={
            "name": "Курс 1",
            "hours": 100,
        },
    )

    assert response.status_code == 302
    course = Course.objects.first()
    course_list_endpoint = reverse("course_detail", args=(course.pk,))
    assert response.url == course_list_endpoint


@pytest.mark.django_db
def test_cant_create_course_without_permission(user):
    c = Client()

    c.login(username='user', password='password')

    assert not user.get_all_permissions()

    course_create_endpoint = reverse("course_create")
    response = c.post(
        course_create_endpoint,
        data={
            "name": "Курс 1",
            "hours": 100,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert Course.objects.count() == 0



