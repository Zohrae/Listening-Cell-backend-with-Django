# Generated by Django 4.1.13 on 2024-05-25 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0032_alter_conseiller_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conseiller',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
