# Generated by Django 3.0.1 on 2020-06-08 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_auto_20200323_2048'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='pro_delievery_charges',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='pro_price',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='pro_total_price',
            field=models.IntegerField(default=1),
        ),
    ]
