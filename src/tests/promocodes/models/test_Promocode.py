import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from promocodes.models import Promocode


@pytest.mark.django_db
def test_cant_edit_promocode_name():

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount')

    with pytest.raises(ValidationError) as e:
        promocode.name = 'PROMOCODE EDITED NAME'
        promocode.save()

    promocode.refresh_from_db()
    assert promocode.name == 'PROMOCODE'
    assert e.value.message == "Запрещено изменять название промокода. Создайте новый промокод, если хотите другое название."


@pytest.mark.django_db
def test_saving_in_uppercase():

    promocode = Promocode.objects.create(name='promocode', type='additional_discount')
    promocode.refresh_from_db()

    assert promocode.name == 'PROMOCODE'


@pytest.mark.django_db
def test_cant_save_two_promocodes_with_equal_name_in_uppercase():
    with transaction.atomic():
        promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount')
    with transaction.atomic():
        with pytest.raises(IntegrityError) as e:
            promocode2 = Promocode.objects.create(name='promocode', type='additional_discount')

    assert Promocode.objects.count() == 1


