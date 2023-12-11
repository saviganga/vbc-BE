# Generated by Django 3.2.9 on 2023-12-03 17:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_auto_20231203_0741'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessLeads',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('lead_type', models.CharField(max_length=50)),
                ('fields', models.JSONField(default=dict)),
                ('journey', models.JSONField(default=list)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='business.businessprofile')),
            ],
            options={
                'ordering': ['-added_on'],
            },
        ),
    ]
