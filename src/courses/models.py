from django.db.models import Model, DateTimeField, CharField, PositiveIntegerField, \
    BooleanField, JSONField, DateField, FloatField
from django.urls import reverse


class CoursesVersion(Model):
    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    table = JSONField(verbose_name='Таблица')

    valid = BooleanField(default=None, verbose_name='Валидна', blank=True, null=True)
    actual = BooleanField(default=False, verbose_name='Актуальная')

    class Meta:
        verbose_name = 'Версия курсов'
        verbose_name_plural = 'Версии курсов'

    def __str__(self):
        return f'Версия сводной таблицы курсов от {self.created_at}'

    def __repr__(self):
        return f'CoursesVersion({self.created_at})'


class ErrorLog(Model):
    created_at = DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    errors = JSONField(verbose_name='Ошибки')

    class Meta:
        verbose_name = 'Лог ошибок'
        verbose_name_plural = 'Логи ошибок'

    def __str__(self):
        return f'Лог ошибок от {self.created_at}'

    def __repr__(self):
        return f'ErrorLog({self.created_at})'

    def get_absolute_url(self):
        return reverse('courses_error_log', kwargs={'pk': self.pk})


class PricesHistory(Model):
    dt = DateField(verbose_name='Дата')

    notion_id = CharField(max_length=100, verbose_name='ID страницы в Notion')
    product_name = CharField(max_length=200, verbose_name='Название продукта')

    full_price = PositiveIntegerField(verbose_name='Полная цена', null=True, blank=True)
    discount_percent = FloatField(verbose_name='Процент скидки', null=True, blank=True)
    price_with_discount = PositiveIntegerField(verbose_name='Цена со скидкой', null=True, blank=True)
    price_per_month_with_discount = FloatField(verbose_name='Цена в месяц со скидкой', null=True, blank=True)
    price_per_month_without_discount = FloatField(verbose_name='Цена в месяц без скидки', null=True, blank=True)

    class Meta:
        verbose_name = 'Запись истории цен'
        verbose_name_plural = 'Записи истории цен'

    def __str__(self):
        return f'Запись истории цен от {self.dt}'

    def __repr__(self):
        return f'PricesHistory({self.dt}, {self.product_name})'

