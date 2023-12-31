import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from promocodes.models import Promocode


@pytest.mark.django_db
def test_cant_edit_promocode_name():

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)

    with pytest.raises(ValidationError) as e:
        promocode.name = 'PROMOCODE EDITED NAME'
        promocode.save()

    promocode.refresh_from_db()
    assert promocode.name == 'PROMOCODE'
    assert e.value.message == "Запрещено изменять название промокода. Создайте новый промокод, если хотите другое название."


@pytest.mark.django_db
def test_saving_in_uppercase():

    promocode = Promocode.objects.create(name='promocode', type='additional_discount', discount=10)
    promocode.refresh_from_db()

    assert promocode.name == 'PROMOCODE'


@pytest.mark.django_db
def test_cant_save_two_promocodes_with_equal_name_in_uppercase():
    with transaction.atomic():
        promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount', discount=10)
    with transaction.atomic():
        with pytest.raises(ValidationError) as e:
            promocode2 = Promocode.objects.create(name='promocode', type='additional_discount', discount=10)

    assert Promocode.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "discount_type, discount",
    (
        ("additional_discount", -50),
        ("additional_discount", 0),
        ("additional_discount", 101),
        ("additional_discount", None),
        ("fix_discount", -50),
        ("fix_discount", 0),
        ("fix_discount", 101),
        ("fix_discount", None),
        ("additional_price", -1),
        ("additional_price", 0),
        ("additional_price", 8888888),
    )
)
def test_promocode_discount_validation(discount_type, discount):
    with pytest.raises(ValidationError) as e:
        Promocode.objects.create(name='PROMOCODE', type=discount_type, discount=discount)

    assert Promocode.objects.count() == 0


