# Generated by Django 5.1.5 on 2025-01-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_expenselimit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenselimit',
            name='daily_expense_limit',
            field=models.IntegerField(default=0),
        ),
    ]
