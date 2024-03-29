# Generated by Django 4.1.7 on 2023-07-04 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_meetups_news'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_be_author',
            field=models.BooleanField(default=False, help_text='Czy wniosek na autora został rozpatrzony pozytywnie.', verbose_name='Czy moż być autorem'),
        ),
    ]
