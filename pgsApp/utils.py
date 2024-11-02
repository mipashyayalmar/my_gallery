# pgsApp/utils.py

from .models import Notification

def create_notification(notification_type, user, message):
    Notification.objects.create(
        notification_type=notification_type,
        user=user,
        message=message
    )
