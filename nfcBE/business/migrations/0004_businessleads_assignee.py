# Generated by Django 3.2.9 on 2023-12-05 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0003_businessleads'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessleads',
            name='assignee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='business.businessmember'),
        ),
    ]