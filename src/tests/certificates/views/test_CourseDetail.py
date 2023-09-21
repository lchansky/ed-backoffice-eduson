import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import user


@pytest.mark.django_db
def test_show_course(user_with_courses_permissions, course):
    c = Client()
    assert c.login(username='user', password='password')
    course_detail_endpoint = reverse("course_detail", args=(course.pk,))

    response = c.get(course_detail_endpoint)

    assert response.status_code == 200
    assert response.context['course'] == course
    assert response.template_name == ['certificates/course_detail.html']


@pytest.mark.django_db
def test_cant_view_course_without_login(course):
    c = Client()

    course_detail_endpoint = reverse("course_detail", args=(course.pk,))

    response = c.get(course_detail_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={course_detail_endpoint}'


@pytest.mark.django_db
def test_cant_view_course_without_permission(user, course):
    c = Client()
    c.login(username='user', password='password')

    course_detail_endpoint = reverse("course_detail", args=(course.pk,))

    response = c.get(course_detail_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('home')
