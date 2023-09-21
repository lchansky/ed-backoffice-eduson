import datetime

import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import user



@pytest.mark.django_db
def test_cant_view_courses_list_without_login(course):
    c = Client()

    course_list_endpoint = reverse("course_list")

    response = c.get(course_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={course_list_endpoint}'


@pytest.mark.django_db
def test_cant_view_courses_list_without_permission(user, course):
    c = Client()
    c.login(username='user', password='password')

    course_list_endpoint = reverse("course_list")

    response = c.get(course_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('home')
