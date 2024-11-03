# Generated by Django 5.1.2 on 2024-11-03 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement01', '0010_alter_generalquestion_question_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SKUSpecificQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('question_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('file', 'File Upload'), ('date', 'Date')], max_length=50)),
                ('rfp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sku_specific_questions', to='procurement01.rfp')),
            ],
        ),
    ]