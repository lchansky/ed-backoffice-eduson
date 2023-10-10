import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import (
    Model,
    CharField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    FloatField,
    DO_NOTHING,
    DateField,
    IntegerField,
)
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Promocode(Model):
    TYPE_CHOICES = (
        ('additional_discount', 'Дополнительная скидка в процентах'),
        ('fix_discount', 'Фиксированная скидка в процентах'),
        ('additional_price', 'Дополнительная скидка в рублях'),
        ('consultation', 'Дополнительная консультация'),
        ('free_course', 'Бесплатный курс'),
    )

    name = CharField(max_length=50, unique=True, verbose_name='Название')
    type = CharField(max_length=50, verbose_name='Тип', choices=TYPE_CHOICES)
    discount = FloatField(verbose_name='Скидка', blank=True, null=True)
    deadline = DateField(verbose_name='Дата истечения', blank=True, null=True)
    is_active = BooleanField(default=True, verbose_name='Активен')

    course_title = CharField(max_length=200, verbose_name='Название курса', blank=True, null=True)

    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = DateTimeField(auto_now=True, verbose_name='Дата изменения')
    created_by = ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True,
                            verbose_name='Кем создан', related_name='created_promocodes')
    updated_by = ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True,
                            verbose_name='Кем изменен', related_name='updated_promocodes')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_discount_display(self):
        if self.type in ('additional_discount', 'fix_discount'):
            return f'{self.discount} %'
        elif self.type in ('additional_price',):
            return f'{self.discount} руб.'
        else:
            return self.discount

    def full_clean(self, *args, **kwargs):
        if self.discount is not None:
            if self.type in ('additional_discount', 'fix_discount') and not (0 < self.discount < 100):
                raise ValidationError("Скидка в процентах должна быть в диапазоне от 0 до 100")
            if self.type == 'additional_price' and not (0 < self.discount < 1000000):
                raise ValidationError("Скидка в рублях должна быть в диапазоне от 0 до 1.000.000")
        elif self.discount is None and self.type in ('additional_discount', 'fix_discount', 'additional_price'):
            raise ValidationError("Скидка не может быть пустой.")
        if self.type == 'free_course' and not self.course_title:
            raise ValidationError(
                "Для промокода с типом 'Бесплатный курс' необходимо указать название курса."
            )
        if self.pk:
            old_name = self.__class__.objects.get(pk=self.pk).name
            if old_name != self.name:
                raise ValidationError("Запрещено изменять название промокода. "
                                      "Создайте новый промокод, если хотите другое название.")
        return super().full_clean(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name.upper()
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse('promocode_detail', kwargs={'pk': self.pk})

    @property
    def is_expired(self):
        if self.deadline and self.deadline < timezone.now().date():
            return True
        return False


class PromocodeRequest(Model):
    dt = DateTimeField(auto_now_add=True, verbose_name='Дата и время запроса')

    uuid = CharField(max_length=50, verbose_name='UUID', blank=True, null=True)
    yandex_client_id = CharField(max_length=50, verbose_name='yandex_client_id', blank=True, null=True)

    promocode_name = CharField(max_length=50, verbose_name='Промокод')
    promocode_type = CharField(max_length=50, verbose_name='Тип промокода', blank=True, null=True)
    promocode_discount = FloatField(verbose_name='Скидка промокода', blank=True, null=True)
    promocode_deadline = DateField(verbose_name='Дата истечения промокода', blank=True, null=True)

    response_status_code = IntegerField(verbose_name='Код ответа', blank=True, null=True)

    class Meta:
        verbose_name = 'Запрос промокода'
        verbose_name_plural = 'Запросы промокодов'

    def __str__(self):
        return f'Запрос промокода {self.dt}, промокод {self.promocode_name}, UUID {self.uuid}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.promocode_name != 'XQECG9RHJG4LBJ87PR3C':
            super().save(force_insert, force_update, using, update_fields)
