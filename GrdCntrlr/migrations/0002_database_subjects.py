# Generated by Django 4.0.4 on 2022-06-02 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GrdCntrlr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='database',
            name='subjects',
            field=models.TextField(default=''),
        ),
    ]
