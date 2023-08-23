import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from tests.conftest import user
from promocodes.models import Promocode


@pytest.mark.django_db
def test_edit_promocode_with_permission(user):
    c = Client()

    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')

    c.login(username='user', password='password')

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount')

    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))
    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': 'fix_discount',
            'name': 'PROMOCODE',
            'discount': 0.5,
            'deadline': '',
            'is_active': True,
        },
    )
    promocode.refresh_from_db()

    assert response.status_code == 302
    promocode_detail_endpoint = reverse("promocode_detail", args=(promocode.pk,))
    assert response.url == promocode_detail_endpoint
    assert promocode.type == 'fix_discount'


@pytest.mark.django_db
def test_edit_promocode_without_permission(user):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount')

    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))
    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': 'fix_discount',
            'name': 'PROMOCODE',
            'discount': 0.5,
            'deadline': '',
            'is_active': True,
        },
    )
    promocode.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse('promocode_list')
    assert promocode.type == 'additional_discount'
