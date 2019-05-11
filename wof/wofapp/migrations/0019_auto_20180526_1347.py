# Generated by Django 2.0 on 2018-05-26 13:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wofapp', '0018_auto_20180522_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comentario',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='denuncia',
            name='data',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='data_cadastro',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]