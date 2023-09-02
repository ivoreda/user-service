from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from . import models

# Register your models here.

admin.site.register(models.CustomUser)
admin.site.register(models.Profile)
admin.site.register(models.EmailVerificationLogs)
admin.site.register(models.PasswordRecoveryLogs)

admin.site.register(models.ImageTestModel)


class BecomeAHostNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')

    def message(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:99Apartment_user_notification_change', args=[obj.pk]), obj.message)


admin.site.register(models.BecomeAHostNotification,
                    BecomeAHostNotificationAdmin)
