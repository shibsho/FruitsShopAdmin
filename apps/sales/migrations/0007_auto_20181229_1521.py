# Generated by Django 2.1.4 on 2018-12-29 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_sale_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='number',
            new_name='item_num',
        ),
        migrations.AlterField(
            model_name='sale',
            name='amount',
            field=models.PositiveIntegerField(
                editable=False, verbose_name='売上'),
        ),
    ]
