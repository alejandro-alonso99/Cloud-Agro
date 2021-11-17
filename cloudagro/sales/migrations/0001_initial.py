# Generated by Django 3.2.7 on 2021-11-01 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('client', models.CharField(max_length=250)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('brute_kg', models.IntegerField(default=0)),
                ('desbaste', models.IntegerField(default=0)),
                ('total_animals', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('pagado', 'Pagado'), ('por pagar', 'Por pagar')], default='por pagar', max_length=15)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='SaleRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoría', models.CharField(choices=[('ternero', 'Ternero'), ('ternera', 'Ternera'), ('novillo', 'Novillo'), ('vaquillona', 'Vaquillona'), ('vaca', 'Vaca')], default='ternero', max_length=500)),
                ('cantidad', models.IntegerField(default=0)),
                ('precio_por_kg', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('iva', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.sales')),
            ],
            options={
                'ordering': ('categoría',),
            },
        ),
    ]
