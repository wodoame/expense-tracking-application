# Generated by Django 5.1.2 on 2025-01-15 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_category_name_alter_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
