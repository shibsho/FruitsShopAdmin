# Generated by Django 2.1.4 on 2018-12-27 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='amount',
            field=models.PositiveIntegerField(editable=False, verbose_name='売上'),
        ),
    ]
