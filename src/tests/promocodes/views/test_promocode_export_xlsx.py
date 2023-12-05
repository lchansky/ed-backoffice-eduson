import pytest
from django.test import Client
from django.urls import reverse

from promocodes.models import Promocode


@pytest.mark.django_db
def test_cant_export_without_permission(user):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    promocode_export_xlsx_endpoint = reverse("promocode_export_xlsx")
    response = c.get(promocode_export_xlsx_endpoint)

    assert response.status_code == 302
    assert response.url == reverse("home")
    assert Promocode.objects.count() == 0
