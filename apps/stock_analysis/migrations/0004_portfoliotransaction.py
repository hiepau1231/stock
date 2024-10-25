# Generated by Django 5.0.2 on 2024-10-26 02:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_analysis', '0003_alter_portfolio_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('BUY', 'Mua vào'), ('SELL', 'Bán ra')], max_length=10)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_analysis.portfolio')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock_analysis.stock')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
