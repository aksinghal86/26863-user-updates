# Generated by Django 4.1 on 2024-11-13 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientUpdates', '0002_alter_pws_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pws',
            name='row_names',
            field=models.BigAutoField(db_column='row_names', primary_key=True, serialize=False),
        ),
    ]
