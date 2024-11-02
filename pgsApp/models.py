from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from PIL import Image
from django.contrib.auth.models import User


from django.db import models
from django.utils import timezone
from PIL import Image
from django.contrib.auth.models import User

class Gallery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_path = models.ImageField(upload_to='images')
    thumbnail_path = models.ImageField(upload_to='thumbnails')
    delete_flag = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)
    caption = models.TextField(blank=True, null=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Uploaded Images"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.thumbnail_path:
            img = Image.open(self.image_path.path)
            img.thumbnail((150, 150))
            thumbnail_io = BytesIO()
            img.save(thumbnail_io, format='JPEG')
            self.thumbnail_path.save(
                f"thumb_{self.image_path.name}",
                ContentFile(thumbnail_io.getvalue()),
                save=False
            )
            super().save(*args, **kwargs)

    def create_thumbnail(self):
        """Create a thumbnail for the uploaded image."""
        imag = Image.open(self.image_path.path)
        width, height = imag.size
        if width > 640:
            width = 640
        if height > 480:
            height = 480
        output_size = (width, height)
        imag.thumbnail(output_size)
        imag.save(self.thumbnail_path.path)

    def delete(self, *args, **kwargs):
        """Delete image and thumbnail files from storage."""
        storage, path = self.image_path.storage, self.image_path.path
        storage.delete(path)
        storage, path = self.thumbnail_path.storage, self.thumbnail_path.path
        super(Gallery, self).delete(*args, **kwargs)
        storage.delete(path)


class UserInteraction(models.Model):
    INTERACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'image')  # A user can only interact with an image once

    def __str__(self):
        return f"{self.user.username} {self.interaction_type}d {self.image.caption[:20]}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    ALL_USERS = 'all'
    SPECIFIC_USER = 'specific'
    notification_type = models.CharField(max_length=10)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='specific_notifications')

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notifications")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="user_notifications")
    deleted = models.BooleanField(default=False)  # Tracks if the user has "deleted" the notification

    class Meta:
        unique_together = ('user', 'notification')
