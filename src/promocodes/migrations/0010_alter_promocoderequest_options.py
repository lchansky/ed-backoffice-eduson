# Generated by Django 4.2.2 on 2023-09-22 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promocodes', '0009_promocoderequest_yandex_client_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='promocoderequest',
            options={'verbose_name': 'Запрос промокода', 'verbose_name_plural': 'Запросы промокодов'},
        ),
    ]
