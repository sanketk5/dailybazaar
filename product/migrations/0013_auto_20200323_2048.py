# Generated by Django 3.0.1 on 2020-03-23 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20200323_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.FloatField(default=0.0),
        ),
    ]
