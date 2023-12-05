import datetime

import pytest
from django.test import Client
from django.urls import reverse

from certificates.models import Certificate



@pytest.mark.django_db
def test_cant_view_certificates_list_without_login(course):
    c = Client()

    Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)
    certificate_list_endpoint = reverse("certificate_list")

    response = c.get(certificate_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={certificate_list_endpoint}'


@pytest.mark.django_db
def test_cant_view_certificates_list_without_permission(user, course):
    c = Client()
    c.login(username='user', password='password')

    Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)
    certificate_list_endpoint = reverse("certificate_list")

    response = c.get(certificate_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('home')
