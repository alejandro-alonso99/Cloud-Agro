# Generated by Django 3.2.7 on 2021-10-23 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Purchases',
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
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Terneros', max_length=500, unique=True)),
                ('slug', models.SlugField(max_length=250, unique_for_date='date')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='purchases.purchases')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
