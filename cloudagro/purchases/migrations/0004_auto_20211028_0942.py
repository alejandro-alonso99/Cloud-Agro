# Generated by Django 3.2.7 on 2021-10-28 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0003_alter_animal_iva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='iva',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='animal',
            name='precio_por_kg',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
