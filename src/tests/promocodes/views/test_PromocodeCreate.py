import pytest
from django.test import Client
from django.urls import reverse

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
def test_course_title_required_for_type_free_course(user_with_promocodes_permissions, course_title, count_created):
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


@pytest.mark.django_db
def test_cant_create_two_promocodes_with_equal_name_in_uppercase(user_with_promocodes_permissions):
    c = Client()
    c.login(username='user', password='password')

    promocode_create_endpoint = reverse("promocode_create")
    response1 = c.post(
        promocode_create_endpoint,
        data={
            'type': "additional_discount",
            'name': 'PROMOCODE',
            'is_active': True,
            'discount': 10,
        },
    )
    promocode1 = Promocode.objects.get(name='PROMOCODE')
    response2 = c.post(
        promocode_create_endpoint,
        data={
            'type': "additional_discount",
            'name': 'promocode',
            'is_active': True,
            'discount': 10,
        },
    )

    assert response1.status_code == 302
    assert response1.url == reverse('promocode_detail', args=(promocode1.pk,))
    assert Promocode.objects.count() == 1
    assert response2.status_code == 200
    assert hasattr(response2.context['form'], 'errors')


@pytest.mark.django_db
def test_cant_create_promocode_with_deadline_in_past(user_with_promocodes_permissions):
    c = Client()
    c.login(username='user', password='password')

    promocode_create_endpoint = reverse("promocode_create")
    response = c.post(
        promocode_create_endpoint,
        data={
            'type': "additional_discount",
            'name': 'PROMOCODE',
            'is_active': True,
            'deadline': '2020-01-01',
            'discount': 10,
        },
    )

    assert response.status_code == 200
    assert hasattr(response.context['form'], 'errors')
    assert Promocode.objects.count() == 0


@pytest.mark.django_db
def test_cant_create_promocode_without_permission(user):
    c = Client()

    assert not user.get_all_permissions()

    c.login(username='user', password='password')

    promocode_create_endpoint = reverse("promocode_create")
    response = c.post(
        promocode_create_endpoint,
        data={
            'type': "additional_discount",
            'name': 'PROMOCODE',
            'is_active': True,
            'discount': 10,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("promocode_list")
    assert Promocode.objects.count() == 0


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
def test_wrong_discount_value(user_with_promocodes_permissions, discount_type, discount):
    c = Client()
    c.login(username='user', password='password')

    promocode_create_endpoint = reverse("promocode_create")
    response = c.post(
        promocode_create_endpoint,
        data={
            'name': 'PROMOCODE',
            'type': discount_type,
            'discount': discount,
        },
    )

    assert response.status_code == 200
    assert hasattr(response.context['form'], 'errors')
    assert Promocode.objects.count() == 0
