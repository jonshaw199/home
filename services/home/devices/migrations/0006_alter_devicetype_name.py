# Generated by Django 4.2 on 2024-10-16 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_light_brightness_light_color_light_is_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
