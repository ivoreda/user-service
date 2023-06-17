from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

USER_TYPE = (('Host', 'Host'),
             (''))


"""
create user types for users and hosts
users interact with the frontend while
hosts interact with the host dashboard

there are also admin or superuser users
that interact with the admin panel
"""


"""
users can apply to become hosts
an admin will see the request and the admin is
able to change the user type from regular user to host

then on the host login, we will check if the user_type is host
in order for the personto login to that platform
"""



class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    username = models.CharField(max_length=20, unique=True)
    hobbies = models.TextField(default='Hobbies', blank=True, null=True)
    interests = models.TextField(default='Interests', blank=True, null=True)
    isVerified = models.BooleanField(default=False)
    profile_picture = CloudinaryField('profile picture', null=True, default=None, blank=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.username

    @property
    def image_url(self):
        return (
            f"https://res.cloudinary.com/dpoix2ilz/{self.profile_picture}"
        )


PROFILE_TYPE = (('Tenant', 'Tenant'),
                ('Landlord', 'Landlord'),)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency_preference = models.CharField(default='NGN')
    profile_type = models.CharField(choices=PROFILE_TYPE, default='Tenant', max_length=255)
    reason_for_deactivation = models.TextField(default='')

    @receiver(post_save, sender=CustomUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=CustomUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self) -> str:
        return self.user.first_name + " " + self.user.last_name

class EmailVerificationLogs(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    isUsed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.email

class PasswordRecoveryLogs(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    isUsed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.email