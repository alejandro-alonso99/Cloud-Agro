# Generated by Django 3.2.7 on 2022-04-26 13:49

from django.db import migrations, models
import expenses.models


class Migration(migrations.Migration):

    dependencies = [
        ('land', '0002_alter_land_campaign'),
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expenses',
            name='campo',
        ),
        migrations.AddField(
            model_name='expenses',
            name='campana',
            field=models.ForeignKey(default=expenses.models.get_sentinel_campaign_id, on_delete=models.SET(expenses.models.get_sentinel_campaign), to='land.campaign'),
        ),
    ]
