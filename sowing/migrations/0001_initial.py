# Generated by Django 3.2.7 on 2022-04-20 15:07

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('land', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SowingPurchases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('factura', models.CharField(blank=True, max_length=100, null=True)),
                ('proveedor', models.CharField(max_length=100)),
                ('producto', models.CharField(max_length=100)),
                ('precio_lt_kg_usd', models.FloatField(default=0)),
                ('lt_kg', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('pagado', 'Pagado'), ('por pagar', 'Por pagar')], default='por pagar', max_length=50)),
                ('tipo_cambio', models.FloatField(default=0)),
                ('iva', models.FloatField(default=0)),
                ('campaña', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='land.campaign')),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='land.land')),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Other_Expenses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='land.lote')),
            ],
        ),
        migrations.CreateModel(
            name='Labors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('numero', models.IntegerField()),
                ('costo_ha', models.FloatField(default=0)),
                ('nombre', models.CharField(max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='land.lote')),
            ],
        ),
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('numero', models.IntegerField()),
                ('lt_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('producto', models.CharField(default='glifosato', max_length=30)),
                ('tipo', models.CharField(choices=[('agroquímicos', 'Agroquímicos'), ('fertilizante', 'Fertilizante'), ('semillas', 'Semillas')], default='agroquímicos', max_length=50)),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='land.lote')),
            ],
        ),
    ]
