# Generated by Django 4.2 on 2024-10-10 02:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Routine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('triggers', models.TextField(blank=True, null=True)),
                ('repeat_interval', models.DurationField(blank=True, null=True)),
                ('eval_condition', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='routines', to='core.location')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('type', models.CharField(max_length=100)),
                ('eval_params', models.TextField(blank=True, null=True)),
                ('routine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='routines.routine')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]