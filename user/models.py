from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=20)
    hobbies = models.JSONField(default={})

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'phone_number'

    def __str__(self) -> str:
        return self.username