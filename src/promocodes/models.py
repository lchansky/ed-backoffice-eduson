from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    CharField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    FloatField,
    DO_NOTHING, DateField,
)

User = get_user_model()


class Promocode(Model):
    TYPE_CHOICES = (
        ('additional_discount', 'Дополнительная скидка в процентах'),
        ('fix_discount', 'Фиксированная скидка в процентах'),
        ('additional_price', 'Дополнительная скидка в рублях'),
        ('consultation', 'Дополнительная консультация'),
        ('free_course', 'Бесплатный курс'),
    )

    code = CharField(primary_key=True, max_length=50, unique=True, verbose_name='Промокод')
    type = CharField(max_length=50, verbose_name='Тип', choices=TYPE_CHOICES)
    discount = FloatField(verbose_name='Скидка', blank=True, null=True)
    deadline = DateField(verbose_name='Дата истечения', blank=True, null=True)
    is_active = BooleanField(default=True, verbose_name='Активен')

    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = DateTimeField(auto_now=True, verbose_name='Дата изменения')
    created_by = ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True,
                            verbose_name='Кем создан', related_name='created_promocodes')
    updated_by = ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True,
                            verbose_name='Кем изменен', related_name='updated_promocodes')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

    def __str__(self):
        return self.code
