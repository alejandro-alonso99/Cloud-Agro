# Generated by Django 3.2.7 on 2022-09-05 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('funds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundmanualmove',
            name='description',
            field=models.CharField(default='movimiento', max_length=250),
        ),
    ]
