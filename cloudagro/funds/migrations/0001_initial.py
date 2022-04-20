# Generated by Django 3.2.7 on 2022-04-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FundManualMove',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia')], default='efectivo', max_length=500)),
                ('action', models.CharField(choices=[('agregar', 'Agregar'), ('quitar', 'Quitar')], default='agregar', max_length=250)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]
