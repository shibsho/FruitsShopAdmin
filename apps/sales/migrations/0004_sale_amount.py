# Generated by Django 2.1.4 on 2018-12-27 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_remove_sale_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='amount',
            field=models.PositiveIntegerField(default=33, editable=False, verbose_name='売上'),
            preserve_default=False,
        ),
    ]
