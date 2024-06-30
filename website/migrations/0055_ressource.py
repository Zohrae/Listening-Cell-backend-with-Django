# Generated by Django 4.1.13 on 2024-06-11 18:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0054_observation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ressource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=100)),
                ('dateAjoutRessource', models.DateField(default=django.utils.timezone.now)),
                ('description', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('url', models.URLField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Ressources',
            },
        ),
    ]
