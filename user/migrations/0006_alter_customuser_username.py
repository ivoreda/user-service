# Generated by Django 4.2.1 on 2023-06-12 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0005_profile_profile_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
