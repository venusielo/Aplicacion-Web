# Generated by Django 5.1.3 on 2024-11-21 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacionING', '0009_task_completed_alter_task_assigned_to_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='assigned_to',
        ),
    ]
