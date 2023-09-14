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
    business_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    username = models.CharField(max_length=20, unique=True, blank=True, null=True)
    hobbies = models.TextField(default='Hobbies', blank=True, null=True)
    about = models.TextField(default='about', blank=True, null=True)

    occupation = models.CharField(default='occupation', blank=True, null=True)
    location = models.CharField(default='location', blank=True, null=True)


    interests = models.TextField(default='Interests', blank=True, null=True)
    isVerified = models.BooleanField(default=False)

    profile_picture = models.ImageField(blank=True, null=True)


    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name


PROFILE_TYPE = (('Guest', 'Guest'),
                ('Host', 'Host'),)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency_preference = models.CharField(default='NGN')
    profile_type = models.CharField(choices=PROFILE_TYPE, default='Guest', max_length=255)
    has_made_host_request = models.BooleanField(default=False)
    reason_for_deactivation = models.TextField(default='')
    isActiveHost = models.BooleanField(default=False)

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


class BecomeAHostNotification(models.Model):
    user = models.CharField(max_length=30)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.user


class ImageTestModel(models.Model):
    image = models.ImageField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
