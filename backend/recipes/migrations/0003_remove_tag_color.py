# Generated by Django 5.1.5 on 2025-02-02 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_user_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='color',
        ),
    ]
