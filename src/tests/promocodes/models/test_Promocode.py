import pytest
from django.core.exceptions import ValidationError

from promocodes.models import Promocode


@pytest.mark.django_db
def test_cant_edit_promocode_name(user):

    promocode = Promocode.objects.create(name='PROMOCODE', type='additional_discount')

    with pytest.raises(ValidationError) as e:
        promocode.name = 'PROMOCODE EDITED NAME'
        promocode.save()

    promocode.refresh_from_db()
    assert promocode.name == 'PROMOCODE'
    assert e.value.message == "Запрещено изменять название промокода. Создайте новый промокод, если хотите другое название."