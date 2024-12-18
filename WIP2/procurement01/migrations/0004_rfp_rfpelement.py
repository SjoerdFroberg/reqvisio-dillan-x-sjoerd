# Generated by Django 3.2.25 on 2024-10-13 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('procurement01', '0003_auto_20241013_1951'),
    ]

    operations = [
        migrations.CreateModel(
            name='RFP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('skus', models.ManyToManyField(to='procurement01.SKU')),
            ],
        ),
        migrations.CreateModel(
            name='RFPElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element_type', models.CharField(choices=[('text', 'Text'), ('numeric', 'Numeric Question'), ('open_text', 'Open Text Question'), ('multiple_choice', 'Multiple Choice Question')], max_length=20)),
                ('content', models.TextField(blank=True, null=True)),
                ('is_sku_related', models.BooleanField(default=False)),
                ('multiple_choice_options', models.JSONField(blank=True, null=True)),
                ('rfp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='procurement01.rfp')),
            ],
        ),
    ]
