# Generated by Django 4.2.2 on 2023-07-14 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snsapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='作成日'),
        ),
    ]
