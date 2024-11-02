from django.contrib import admin
from .models import Gallery, UserInteraction, Notification

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_path', 'thumbnail_path', 'delete_flag', 'date_added', 'date_created', 'caption', 'likes', 'dislikes')
    search_fields = ('caption',)
    list_filter = ('delete_flag', 'date_added')
    readonly_fields = ('date_created',)


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'interaction_type')
    search_fields = ('user__username', 'image__caption')
    list_filter = ('interaction_type',)

# pgsApp/admin.py

# pgsApp/admin.py

from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'created_at')
    list_filter = ('notification_type', 'user')
    search_fields = ('message',)

admin.site.register(Notification, NotificationAdmin)
