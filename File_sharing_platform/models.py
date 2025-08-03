from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
import boto3
from django.core.files.storage import default_storage

class Category(models.Model):
    category_name = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name
    
class File(models.Model):
    title = models.TextField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file_thumbnail = models.ImageField(upload_to='thumbnails/%y/%m/%d', blank=True, null=True)
    file_description = models.TextField(blank=True, null=True)
    file_urls = models.FileField(upload_to='uploads/%y/%m/%d')
    file_status = models.IntegerField(choices=[(0, 'Free'), (1, 'For sales')], default=0)
    file_price = models.PositiveIntegerField(default=0)
    file_downloads = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_presigned_url(self, expires_in=3600):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.file_urls.name},
            ExpiresIn=expires_in
        )

    def get_thumbnail_presigned_url(self, expires_in=3600):
        """Lấy presigned URL cho thumbnail"""
        if self.file_thumbnail and self.file_thumbnail.name:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.file_thumbnail.name},
                ExpiresIn=expires_in
            )
        else:
            # Trả về URL default thumbnail local (không cần presigned URL cho static files)
            return f"{settings.STATIC_URL}images/default.webp"

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "File"
        verbose_name_plural = "Files"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'file']
        ordering = ['-created_at']
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
    
    def __str__(self):
        return f"{self.user.username} - {self.file.title}"

