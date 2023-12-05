import datetime

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from certificates.models import Certificate


@pytest.mark.django_db
def test_create_certificate_with_permission(user, course):
    c = Client()
    permission = Permission.objects.get(codename='add_certificate')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.add_certificate')

    assert c.login(username='user', password='password')

    certificate_create_endpoint = reverse("certificate_create")
    response = c.post(
        certificate_create_endpoint,
        data={
            'date': datetime.date.today().isoformat(),
            'student_fio': 'Вася Пупкин 1111',
            'course': course.pk,
        },
    )

    assert response.status_code == 302
    certificate = Certificate.objects.first()
    certificate_list_endpoint = reverse("certificate_detail", args=(certificate.pk,))
    assert response.url == certificate_list_endpoint


@pytest.mark.django_db
def test_cant_create_certificate_without_permission(user, course):
    c = Client()

    c.login(username='user', password='password')

    assert not user.get_all_permissions()

    certificate_create_endpoint = reverse("certificate_create")
    response = c.post(
        certificate_create_endpoint,
        data={
            'date': datetime.date.today().isoformat(),
            'student_fio': 'Вася Пупкин 1111',
            'course': course.pk,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("certificate_list")
    assert Certificate.objects.count() == 0



