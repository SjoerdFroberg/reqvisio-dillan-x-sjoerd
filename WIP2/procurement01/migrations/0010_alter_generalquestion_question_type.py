# Generated by Django 5.1.2 on 2024-11-01 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement01', '0009_remove_rfp_skus_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalquestion',
            name='question_type',
            field=models.CharField(choices=[('text', 'Text'), ('Single-select', 'Single-select'), ('Multi-select', 'Multi-select'), ('File upload', 'File upload')], max_length=200),
        ),
    ]
