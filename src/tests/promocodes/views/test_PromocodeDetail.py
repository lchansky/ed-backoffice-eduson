from urllib.parse import urlencode

import pytest
from django.test import Client
from django.urls import reverse

from tests.conftest import user
from promocodes.models import Promocode


@pytest.mark.django_db
def test_show_promocode(user):
    c = Client()
    assert c.login(username='user', password='password')
    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_detail_endpoint = reverse("promocode_detail", args=(promocode.pk,))

    response = c.get(promocode_detail_endpoint)

    assert response.status_code == 200
    assert response.context['promocode'] == promocode
    assert response.template_name == ['promocodes/promocode_detail.html']


@pytest.mark.django_db
def test_show_promocode_without_login(user):
    c = Client()

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_detail_endpoint = reverse("promocode_detail", args=(promocode.pk,))

    response = c.get(promocode_detail_endpoint)

    assert response.status_code == 302
    assert response.url == reverse('login') + f'?next={promocode_detail_endpoint}'
