# Generated by Django 4.2.2 on 2023-08-11 10:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Promocode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Промокод')),
                ('type', models.CharField(choices=[('additional_discount', 'Дополнительная скидка в процентах'), ('fix_discount', 'Фиксированная скидка в процентах'), ('additional_price', 'Дополнительная скидка в рублях'), ('consultation', 'Дополнительная консультация'), ('free_course', 'Бесплатный курс')], max_length=50, verbose_name='Тип')),
                ('discount', models.FloatField(verbose_name='Скидка')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_promocodes', to=settings.AUTH_USER_MODEL, verbose_name='Кем создан')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='updated_promocodes', to=settings.AUTH_USER_MODEL, verbose_name='Кем изменен')),
            ],
            options={
                'verbose_name': 'Промокод',
                'verbose_name_plural': 'Промокоды',
            },
        ),
    ]
