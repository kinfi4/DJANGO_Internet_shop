# Generated by Django 3.1 on 2020-10-27 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20201027_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='total_products',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
