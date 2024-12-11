# Generated by Django 4.1.7 on 2024-12-11 07:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0006_remove_user_email_hash_remove_user_hash_time_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=155, null=True)),
                ('author', models.CharField(blank=True, max_length=155, null=True)),
            ],
            options={
                'db_table': 'books',
            },
        ),
        migrations.CreateModel(
            name='BorrowRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Approved'), (3, 'Denied')], default=1)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library_app.books')),
            ],
            options={
                'db_table': 'book_manage',
            },
        ),
        migrations.DeleteModel(
            name='Assets',
        ),
        migrations.DeleteModel(
            name='OTP',
        ),
        migrations.DeleteModel(
            name='Student',
        ),
        migrations.RemoveField(
            model_name='user',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='user',
            name='login_otp',
        ),
        migrations.RemoveField(
            model_name='user',
            name='login_otp_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='new_otp',
        ),
        migrations.RemoveField(
            model_name='user',
            name='otp',
        ),
        migrations.RemoveField(
            model_name='user',
            name='otp_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
        migrations.AddField(
            model_name='user',
            name='is_librarian',
            field=models.BooleanField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email address'),
        ),
        migrations.AddField(
            model_name='borrowrequests',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
