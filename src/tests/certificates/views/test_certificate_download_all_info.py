import datetime

import pytest
from django.test import Client
from django.urls import reverse

from certificates.models import Certificate


@pytest.mark.django_db
def test_cant_view_page_without_permission(user, course):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)

    certificate_download_all_info_view = reverse("certificate_download_all_info")
    response = c.get(certificate_download_all_info_view)

    assert response.status_code == 302
    assert response.url == reverse("home")
