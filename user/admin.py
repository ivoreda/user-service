from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.CustomUser)
admin.site.register(models.EmailVerificationLogs)
admin.site.register(models.PasswordRecoveryLogs)
