# Generated by Django 4.1 on 2024-11-13 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientUpdates', '0005_alter_eurofinsreportsfilenames_row_names_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pfasresult',
            name='row_names',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
