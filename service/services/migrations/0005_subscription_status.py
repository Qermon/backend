# Generated by Django 3.2.16 on 2024-12-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_subscription_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('pending', 'Pending')], default='pending', max_length=10),
        ),
    ]
