# Generated by Django 5.0.2 on 2024-10-25 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_analysis', '0002_alter_stock_company_name_alter_stock_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
