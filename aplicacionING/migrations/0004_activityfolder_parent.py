# Generated by Django 4.2.11 on 2024-11-15 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aplicacionING', '0003_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityfolder',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subactivities', to='aplicacionING.activityfolder'),
        ),
    ]
