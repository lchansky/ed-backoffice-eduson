# Generated by Django 4.2.2 on 2023-08-16 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promocodes', '0004_alter_promocode_options_rename_code_promocode_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromocodeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время запроса')),
                ('uuid', models.CharField(blank=True, max_length=50, null=True, verbose_name='UUID')),
                ('promocode_name', models.CharField(max_length=50, verbose_name='Промокод')),
                ('promocode_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='Тип промокода')),
                ('promocode_discount', models.FloatField(blank=True, null=True, verbose_name='Скидка промокода')),
                ('promocode_deadline', models.DateField(blank=True, null=True, verbose_name='Дата истечения промокода')),
                ('response_status_code', models.CharField(blank=True, max_length=50, null=True, verbose_name='Код ответа')),
            ],
        ),
    ]
