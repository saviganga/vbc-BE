# Generated by Django 3.2.9 on 2023-12-11 12:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0004_businessleads_assignee'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessProfileAnalytics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('team_members', models.IntegerField()),
                ('leads', models.IntegerField()),
                ('converted_leads', models.IntegerField()),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='business.businessprofile')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessMemberAnalytics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('leads', models.IntegerField()),
                ('converted_leads', models.IntegerField()),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('business_member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='business.businessmember')),
            ],
        ),
    ]
