import datetime

import pytest
from django.test import Client
from django.urls import reverse

from certificates.models import Certificate


@pytest.mark.django_db
@pytest.mark.parametrize(
    "image_type",
    [
        "image",
        "printer",
    ]
)
def test_cant_view_page_without_permission(user, course, image_type):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    certificate = Certificate.objects.create(date=datetime.date.today(), student_fio='Василий', course=course)

    certificate_image_view = reverse("certificate_image", args=(certificate.pk, image_type))
    response = c.get(certificate_image_view)

    assert response.status_code == 302
    assert response.url == reverse("home")
