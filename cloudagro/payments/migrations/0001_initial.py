# Generated by Django 3.2.7 on 2021-12-28 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyChecks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('slug', models.SlugField(default='ckeck', max_length=250, unique_for_date='fecha_ingreso')),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=50)),
                ('fecha_deposito', models.DateField()),
                ('banco_emision', models.CharField(choices=[('credicoop', 'Credicoop'), ('supervielle', 'Supervielle'), ('galicia', 'Banco Galicia'), ('frances', 'Banco Frances')], default='galicia', max_length=50)),
                ('numero_cheque', models.IntegerField()),
                ('titular_cheque', models.CharField(max_length=50)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('depositado', 'Depositado'), ('a depositar', 'A depositar'), ('endosado', 'Endosado')], default='a depositar', max_length=50)),
                ('depositado_en', models.CharField(choices=[('credicoop', 'Credicoop'), ('supervielle', 'Supervielle'), ('galicia', 'Banco Galicia'), ('frances', 'Banco Frances')], default='galicia', max_length=50)),
                ('observacion', models.TextField(blank=True, max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-fecha_ingreso',),
            },
        ),
        migrations.CreateModel(
            name='SelfChecks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('slug', models.SlugField(default='ckeck', max_length=250, unique_for_date='fecha_salida')),
                ('fecha_salida', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=50)),
                ('fecha_pago', models.DateField()),
                ('banco_emision', models.CharField(choices=[('credicoop', 'Credicoop'), ('supervielle', 'Supervielle'), ('galicia', 'Banco Galicia'), ('frances', 'Banco Frances')], default='galicia', max_length=50)),
                ('numero_cheque', models.IntegerField()),
                ('titular_cheque', models.CharField(max_length=50)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('pagado', 'Pagado'), ('a pagar', 'A Pagar')], default='a pagar', max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-fecha_salida',),
            },
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('object_id', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tipo', models.CharField(choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia')], default='efectivo', max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='EndorsedChecks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('slug', models.SlugField(default='ckeck', max_length=250, unique_for_date='fecha_ingreso')),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=50)),
                ('fecha_deposito', models.DateField()),
                ('banco_emision', models.CharField(choices=[('credicoop', 'Credicoop'), ('supervielle', 'Supervielle'), ('galicia', 'Banco Galicia'), ('frances', 'Banco Frances')], default='galicia', max_length=50)),
                ('numero_cheque', models.IntegerField()),
                ('titular_cheque', models.CharField(max_length=50)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('depositado', 'Depositado'), ('a depositar', 'A depositar'), ('endosado', 'Endosado')], default='endosado', max_length=50)),
                ('depositado_en', models.CharField(choices=[('credicoop', 'Credicoop'), ('supervielle', 'Supervielle'), ('galicia', 'Banco Galicia'), ('frances', 'Banco Frances')], default='galicia', max_length=50)),
                ('observacion', models.TextField(blank=True, max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-fecha_ingreso',),
            },
        ),
    ]
