# Generated by Django 5.1.2 on 2025-06-06 11:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_weeklyspending_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlySpending',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_start', models.DateField()),
                ('month_end', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monthly_spendings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-total_amount'],
            },
        ),
    ]
