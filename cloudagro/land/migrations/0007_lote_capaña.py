# Generated by Django 3.2.7 on 2022-01-24 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('land', '0006_alter_campaign_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='capaña',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='land.campaign'),
        ),
    ]
