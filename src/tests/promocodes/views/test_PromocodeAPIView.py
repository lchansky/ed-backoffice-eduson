import datetime

import pytest

from django.test import Client
from django.urls import reverse

from promocodes.models import Promocode, PromocodeRequest


@pytest.mark.django_db
def test_return_course_title_for_promocodes_with_type_free_course():
    c = Client()
    promocode = Promocode.objects.create(
        name="PROMOCODE",
        type="free_course",
        deadline=datetime.date.today(),
        is_active=True,
        course_title="Test course",
    )
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    assert response.status_code == 200
    assert response.json().get("course_title") == promocode.course_title


@pytest.mark.django_db
def test_return_course_title_for_promocodes_with_type_not_free_course():
    c = Client()
    promocode = Promocode.objects.create(
        name="PROMOCODE",
        type="additional_discount",
        discount=10,
        deadline=datetime.date.today(),
        is_active=True,
    )
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    assert response.status_code == 200
    assert response.json().get("course_title") is None


@pytest.mark.parametrize(
    "promocode_data",
    (
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "discount": 10,
        },
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "discount": 10,
            "deadline": datetime.date.today(),
            "is_active": True,
        },
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "discount": 10,
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
    assert response.json().get("status") == 200


@pytest.mark.parametrize(
    "promocode_data",
    (
        {
            "name": "PROMOCODE",
            "type": "additional_discount",
            "discount": 10,
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
    assert response.json().get("status") == 201


@pytest.mark.django_db
def test_not_existing_promocode():
    c = Client()
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": "test_name"})

    assert response.status_code == 404
    assert response.json().get("status") == 404


@pytest.mark.django_db
def test_inactive_promocode():
    c = Client()
    promocode = Promocode.objects.create(
        name="PROMOCODE",
        type="additional_discount",
        discount=10,
        is_active=False,
    )
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    assert response.status_code == 201
    assert response.json().get("status") == 201


@pytest.mark.django_db
@pytest.mark.parametrize(
    "promocode_data, response_status_code",
    (
        ({"is_active": False, "deadline": None}, 201),
        ({"is_active": True, "deadline": None}, 200),
        ({"is_active": True, "deadline": datetime.date.today() - datetime.timedelta(days=1)}, 201),
        ({"is_active": True, "deadline": datetime.date.today() + datetime.timedelta(days=1)}, 200),
        ({"is_active": True, "deadline": datetime.date.today()}, 200),
    )
)
def test_promocode_request_created(promocode_data, response_status_code):
    c = Client()
    promocode = Promocode.objects.create(
        name="PROMOCODE",
        type="additional_discount",
        discount=0.1,
        is_active=promocode_data.get("is_active"),
        deadline=promocode_data.get("deadline"),
    )
    api_endpoint = reverse("promocode_api")

    response = c.get(api_endpoint, {"name": promocode.name})

    promocode_requests = PromocodeRequest.objects.order_by("-dt")
    assert response.status_code == response_status_code
    assert promocode_requests.count() == 1
    assert promocode_requests.first().promocode_name == promocode.name
    assert promocode_requests.first().response_status_code == response_status_code
