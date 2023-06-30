from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [

        migrations.RunSQL(
            'ALTER SEQUENCE certificates_certificate_id_seq RESTART WITH 500;'
        ),
    ]
