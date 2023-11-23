# Generated by Django 4.1.7 on 2023-06-19 08:36

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_alter_articleauthor_sample_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articleauthor',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='PL', unique=True, verbose_name='Numer telefonu'),
        ),
    ]