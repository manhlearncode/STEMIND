from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import boto3

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"
    
    def like_count(self):
        return self.likes.count()
    
    def comment_count(self):
        return self.comments.count()
    
    def get_image_presigned_url(self, expires_in=3600):
        """Lấy presigned URL cho ảnh post"""
        if self.image and self.image.name:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.image.name},
                ExpiresIn=expires_in
            )
        return None

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Giáo viên'),
        ('expert', 'Chuyên gia'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lastname = models.CharField(max_length=100, blank=True, verbose_name='Họ')
    firstname = models.CharField(max_length=100, blank=True, verbose_name='Tên')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tuổi')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, verbose_name='Vai trò')
    bio = models.TextField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    
    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        if self.firstname and self.lastname:
            return f"{self.lastname} {self.firstname}"
        return self.user.get_full_name() or self.user.username
    
    def followers_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.user.following.count()
    
    def get_avatar_presigned_url(self, expires_in=3600):
        """Lấy presigned URL cho avatar"""
        if self.avatar and self.avatar.name:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            return s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.avatar.name},
                ExpiresIn=expires_in
            )
        return None

# Signal to create UserProfile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
