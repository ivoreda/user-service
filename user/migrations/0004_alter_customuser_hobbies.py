# Generated by Django 4.2.1 on 2023-05-09 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_customuser_dob_customuser_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="hobbies",
            field=models.JSONField(blank=True, default={}, null=True),
        ),
    ]
