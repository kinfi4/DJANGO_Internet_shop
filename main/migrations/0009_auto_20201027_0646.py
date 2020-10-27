# Generated by Django 3.1 on 2020-10-27 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20201026_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='user_agent',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='User-Agent'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, related_name='related_cart', to='main.CartProduct'),
        ),
    ]
