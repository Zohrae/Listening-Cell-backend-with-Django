# Generated by Django 4.1.13 on 2024-05-08 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='conseiller',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
