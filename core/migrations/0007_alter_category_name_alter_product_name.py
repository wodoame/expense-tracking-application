# Generated by Django 5.1.2 on 2025-01-15 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_category_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=25),
        ),
    ]
