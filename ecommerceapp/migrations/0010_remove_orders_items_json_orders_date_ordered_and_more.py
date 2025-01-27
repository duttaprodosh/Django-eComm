# Generated by Django 4.2.13 on 2024-06-24 11:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0009_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='items_json',
        ),
        migrations.AddField(
            model_name='orders',
            name='date_ordered',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orders',
            name='date_shipped',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='invoice_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='invoice_no',
            field=models.CharField(default=None, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='shipped',
            field=models.BooleanField(default=False),
        ),
    ]
