import datetime

import pytest
from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

from promocodes.models import Promocode


@pytest.mark.django_db
def test_cant_edit_promocode_name(user):
    c = Client()

    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')

    c.login(username='user', password='password')

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)

    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))
    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': promocode.type,
            'name': 'PROMOCODE EDITED NAME',
            'discount': promocode.discount if promocode.discount else '',
            'deadline': promocode.deadline if promocode.deadline else '',
            'is_active': promocode.is_active,
        },
    )
    promocode.refresh_from_db()

    assert promocode.name == 'PROMOCODE'


@pytest.mark.django_db
def test_edit_promocode_with_permission(user):
    c = Client()

    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()

    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')

    c.login(username='user', password='password')

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)

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

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)

    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))
    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': 'fix_discount',
            'name': 'PROMOCODE',
            'discount': 50,
            'deadline': '',
            'is_active': True,
        },
    )
    promocode.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse('promocode_list')
    assert promocode.type == 'additional_discount'


@pytest.mark.parametrize(
    "course_title, was_edited",
    (
        ("Test course", True),
        ("", False),
    ),
    ids=("created_with_course_title", "not_created_without_course_title"),
)
@pytest.mark.django_db
def test_course_title_required_for_type_free_course(user, course_title, was_edited):
    c = Client()
    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()
    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')
    c.login(username='user', password='password')
    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))

    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': 'free_course',
            'name': 'PROMOCODE',
            'discount': '',
            'deadline': '',
            'is_active': True,
            'course_title': course_title,
        },
    )
    promocode.refresh_from_db()

    edited = promocode.type == 'free_course'
    assert edited == was_edited


@pytest.mark.django_db
def test_cant_set_promocode_deadline_in_past(user):
    c = Client()
    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()
    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')
    c.login(username='user', password='password')

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10, deadline=tomorrow)
    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))

    response = c.post(
        promocode_edit_endpoint,
        data={
            'type': 'additional_discount',
            'name': 'PROMOCODE',
            'discount': 10,
            'deadline': '2020-01-01',
        },
    )
    promocode.refresh_from_db()

    assert response.status_code == 200
    assert hasattr(response.context['form'], 'errors')
    assert promocode.deadline == tomorrow


@pytest.mark.django_db
@pytest.mark.parametrize(
    "discount_type, discount",
    (
        ("additional_discount", -50),
        ("additional_discount", 0),
        ("additional_discount", 101),
        ("additional_discount", ''),
        ("fix_discount", -50),
        ("fix_discount", 0),
        ("fix_discount", 101),
        ("fix_discount", ''),
        ("additional_price", -1),
        ("additional_price", 0),
        ("additional_price", 8888888),
    )
)
def test_wrong_discount_value(user, discount_type, discount):
    c = Client()
    permission = Permission.objects.get(codename='change_promocode')
    user.user_permissions.add(permission)
    user.save()
    assert user.get_all_permissions()
    assert user.has_perm(f'{permission.content_type.app_label}.change_promocode')
    c.login(username='user', password='password')

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    promocode_edit_endpoint = reverse("promocode_edit", args=(promocode.pk,))

    response = c.post(
        promocode_edit_endpoint,
        data={
            'name': 'PROMOCODE',
            'type': discount_type,
            'discount': discount,
        },
    )
    promocode.refresh_from_db()

    assert response.status_code == 200
    assert hasattr(response.context['form'], 'errors')
    assert promocode.discount != discount
