import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from tests.conftest import user


@pytest.mark.django_db
def test_edit_course_with_permission(user, course):
    c = Client()

    permission = Permission.objects.get(codename='change_course')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_course')

    c.login(username='user', password='password')

    course_edit_endpoint = reverse("course_edit", args=(course.pk,))
    response = c.post(
        course_edit_endpoint,
        data={
            "name": "Курс измененный",
            "hours": 100,
        },
    )
    course.refresh_from_db()

    assert response.status_code == 302
    course_detail_endpoint = reverse("course_detail", args=(course.pk,))
    assert response.url == course_detail_endpoint
    assert course.name == "Курс измененный"


@pytest.mark.django_db
def test_cant_edit_course_without_permission(user, course):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    course_edit_endpoint = reverse("course_edit", args=(course.pk,))
    old_course_name = course.name
    response = c.post(
        course_edit_endpoint,
        data={
            "name": "Курс измененный",
            "hours": 100,
        },
    )
    course.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse('course_list')
    assert course.name == old_course_name


