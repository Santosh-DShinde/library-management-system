# Generated by Django 4.1.7 on 2023-05-24 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.IntegerField(choices=[(1, 'male'), (2, 'female'), (3, 'other')]),
        ),
    ]