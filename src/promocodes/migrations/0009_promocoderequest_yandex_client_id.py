# Generated by Django 4.2.2 on 2023-08-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promocodes', '0008_alter_promocoderequest_response_status_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocoderequest',
            name='yandex_client_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='yandex_client_id'),
        ),
    ]
