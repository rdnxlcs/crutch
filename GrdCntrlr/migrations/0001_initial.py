# Generated by Django 4.0.4 on 2022-05-31 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=200, verbose_name='Логин')),
                ('password', models.CharField(max_length=200, verbose_name='Пароль')),
                ('checkbox', models.BooleanField(verbose_name='Запоминать')),
            ],
        ),
    ]
