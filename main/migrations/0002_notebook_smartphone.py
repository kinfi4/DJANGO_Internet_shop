# Generated by Django 3.1.2 on 2020-10-12 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Smartphone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(null=True, verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Price')),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='', verbose_name='Image')),
                ('diagonal', models.CharField(max_length=255, verbose_name='Diagonal')),
                ('display_type', models.CharField(max_length=255, verbose_name='Display type')),
                ('resolution', models.CharField(max_length=255, verbose_name='Resolution')),
                ('sd', models.BooleanField(default=True)),
                ('accum_volume', models.CharField(max_length=255, verbose_name='Accumulator volume')),
                ('ram', models.CharField(max_length=255, verbose_name='RAM')),
                ('sd_volume_max', models.CharField(max_length=255, verbose_name='Max volume of memory')),
                ('main_cam_mp', models.CharField(max_length=255, verbose_name='Main camera')),
                ('front_cam_mp', models.CharField(max_length=255, verbose_name='Front camera')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.category', verbose_name='Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(null=True, verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Price')),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='', verbose_name='Image')),
                ('diagonal', models.CharField(max_length=255, verbose_name='Diagonal')),
                ('display_type', models.CharField(max_length=255, verbose_name='Display type')),
                ('processor_frq', models.CharField(max_length=255, verbose_name='Processor frequency')),
                ('ram', models.CharField(max_length=255, verbose_name='RAM')),
                ('video', models.CharField(max_length=255, verbose_name='Video card')),
                ('time_without_charge', models.CharField(max_length=255, verbose_name='Time without charge')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.category', verbose_name='Category')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]