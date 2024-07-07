# Generated by Django 4.2.13 on 2024-06-21 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0005_product_is_sale_product_sale_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sale_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
