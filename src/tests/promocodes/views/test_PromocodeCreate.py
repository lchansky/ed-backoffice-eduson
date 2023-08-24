import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from tests.conftest import user
from promocodes.models import Promocode


@pytest.mark.parametrize(
    "course_title, count_created",
    (
        ("Test course", 1),
        ("", 0),
    ),
    ids=("created_with_course_title", "not_created_without_course_title"),
)
@pytest.mark.django_db
def test_course_title_required_for_type_free_course(user, course_title, count_created):
    c = Client()
    c.login(username='user', password='password')

    promocode_create_endpoint = reverse("promocode_create")
    response = c.post(
        promocode_create_endpoint,
        data={
            'type': "free_course",
            'name': 'PROMOCODE',
            'is_active': True,
            'course_title': course_title,
        },
    )

    assert Promocode.objects.count() == count_created
