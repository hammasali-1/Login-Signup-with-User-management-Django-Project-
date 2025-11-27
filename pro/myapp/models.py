from django.db import models
import os
import uuid

# Create your models here.


def profile_image_path(instance, filename):
    base = 'upload/profile_image'
    ext = os.path.splitext(filename)[1].lower()
    uid = f"{instance.id}_{uuid.uuid4().hex}{ext}"
    return os.path.join(base, uid)

class customers(models.Model):
    username = models.CharField(max_length=21, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to=profile_image_path, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10,
        choices=(
            ('admin','Admin'),
            ('manager','Manager'),
            ('user','User')
        ),
        default='user'
    )
    theme = models.CharField(
        max_length=10,
        choices=(('light','Light'),('dark','Dark')),
        default='light'
    )

    def __str__(self):
        return str(self.username or self.email or self.id)

class SiteInfo(models.Model):
    about_title = models.CharField(max_length=100, default='About Us')
    about_content = models.TextField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=24, null=True, blank=True)
    contact_address = models.CharField(max_length=255, null=True, blank=True)
    contact_description = models.TextField(null=True, blank=True)

class ContactMessage(models.Model):
    user = models.ForeignKey(customers, null=True, blank=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=120, null=True, blank=True)
    username = models.CharField(max_length=64, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
