# Generated by Django 4.2.8 on 2023-12-15 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_alter_priceshistory_discount_percent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='priceshistory',
            name='discount_percent',
            field=models.FloatField(blank=True, null=True, verbose_name='Процент скидки'),
        ),
    ]