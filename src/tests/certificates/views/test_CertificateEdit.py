import datetime

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from certificates.models import Certificate



@pytest.mark.django_db
def test_edit_certificate_with_permission(user, course):
    c = Client()

    permission = Permission.objects.get(codename='change_certificate')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_certificate')

    c.login(username='user', password='password')

    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)

    certificate_edit_endpoint = reverse("certificate_edit", args=(certificate.pk,))
    response = c.post(
        certificate_edit_endpoint,
        data={
            'date': '2023-09-19',
            'student_fio': 'Василий Измененный',
            'course': course.pk,
        },
    )
    certificate.refresh_from_db()

    assert response.status_code == 302
    certificate_detail_endpoint = reverse("certificate_detail", args=(certificate.pk,))
    assert response.url == certificate_detail_endpoint
    assert certificate.student_fio == 'Василий Измененный'


@pytest.mark.django_db
def test_cant_edit_certificate_without_permission(user, course):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)

    certificate_edit_endpoint = reverse("certificate_edit", args=(certificate.pk,))
    response = c.post(
        certificate_edit_endpoint,
        data={
            'date': '2023-09-19',
            'student_fio': 'Василий Измененный',
            'course': course.pk,
        },
    )
    certificate.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse('certificate_list')
    assert certificate.student_fio == 'Василий'


