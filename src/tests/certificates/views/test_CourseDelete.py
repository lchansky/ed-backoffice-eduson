import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from certificates.models import Course
from tests.conftest import user


@pytest.mark.django_db
def test_edit_course_with_permission(user, course):
    c = Client()

    permission = Permission.objects.get(codename='delete_course')
    user.user_permissions.add(permission)
    user.save()

    assert Course.objects.count() == 1
    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.delete_course')

    c.login(username='user', password='password')

    course_delete_endpoint = reverse("course_delete", args=(course.pk,))
    response = c.post(course_delete_endpoint)

    assert response.status_code == 302
    assert response.url == reverse("course_list")
    assert Course.objects.count() == 0


@pytest.mark.django_db
def test_cant_edit_course_without_permission(user, course):
    c = Client()

    assert not user.get_all_permissions()
    assert Course.objects.count() == 1
    c.login(username='user', password='password')

    course_delete_endpoint = reverse("course_delete", args=(course.pk,))
    response = c.post(course_delete_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('course_list')
    assert Course.objects.count() == 1


