import datetime

import pytest

from django.test import Client
from django.urls import reverse

from promocodes.models import Promocode


@pytest.mark.parametrize(
    "promocode_data",
    (
        {"name": "PROMOCODE", "type": "additional_discount"},
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "deadline": datetime.date.today(),
            "is_active": True,
        },
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "deadline": datetime.date.today() + datetime.timedelta(days=1),
        },
    ),
    ids=["without_deadline", "deadline_today", "deadline_tomorrow"],
)
@pytest.mark.django_db
def test_valid_promocode(promocode_data: dict):
    # arrange
    c = Client()
    promocode = Promocode.objects.create(**promocode_data)
    api_endpoint = reverse("promocode_api")

    # act
    response = c.get(api_endpoint, {"name": promocode.name})

    # assert
    assert response.status_code == 200


@pytest.mark.parametrize(
    "promocode_data",
    (
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "deadline": datetime.date.today() - datetime.timedelta(days=1),
        },
    ),
    ids=["deadline_yesterday"],
)
@pytest.mark.django_db
def test_expired_promocode(promocode_data: dict):
    c = Client()
    promocode = Promocode.objects.create(**promocode_data)
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    assert response.status_code == 201


@pytest.mark.django_db
def test_not_existing_promocode():
    c = Client()
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": "test_name"})

    assert response.status_code == 404


@pytest.mark.django_db
def test_inactive_promocode():
    c = Client()
    promocode = Promocode.objects.create(
        name="PROMOCODE",
        type="additional_discount",
        is_active=False,
    )
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    assert response.status_code == 404
