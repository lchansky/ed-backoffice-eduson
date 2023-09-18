import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import user
from promocodes.models import Promocode



@pytest.mark.django_db
def test_cant_view_promocodes_list_without_login():
    c = Client()

    Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_list_endpoint = reverse("promocode_list")

    response = c.get(promocode_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={promocode_list_endpoint}'


@pytest.mark.django_db
def test_cant_view_promocodes_list_without_permission(user):
    c = Client()
    c.login(username='user', password='password')

    Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_list_endpoint = reverse("promocode_list")

    response = c.get(promocode_list_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('home')
