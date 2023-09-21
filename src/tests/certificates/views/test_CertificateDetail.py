import datetime

import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import user
from certificates.models import Certificate


@pytest.mark.django_db
def test_show_certificate(user_with_certificates_permissions, course):
    c = Client()
    assert c.login(username='user', password='password')
    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)
    certificate_detail_endpoint = reverse("certificate_detail", args=(certificate.pk,))

    response = c.get(certificate_detail_endpoint)

    assert response.status_code == 200
    assert response.context['certificate'] == certificate
    assert response.template_name == ['certificates/certificate_detail.html']


@pytest.mark.django_db
def test_cant_view_certificate_without_login(course):
    c = Client()

    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)
    certificate_detail_endpoint = reverse("certificate_detail", args=(certificate.pk,))

    response = c.get(certificate_detail_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={certificate_detail_endpoint}'


@pytest.mark.django_db
def test_cant_view_certificate_without_permission(user, course):
    c = Client()
    c.login(username='user', password='password')

    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)
    certificate_detail_endpoint = reverse("certificate_detail", args=(certificate.pk,))

    response = c.get(certificate_detail_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('home')
