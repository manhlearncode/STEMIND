from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import boto3

class CustomUser(AbstractUser):
    """Custom User model với các trường bổ sung"""
    ROLE_CHOICES = [
        ('teacher', 'Giáo viên'),
        ('expert', 'Chuyên gia'),
    ]
    
    # Thêm các trường mới
    lastname = models.CharField(max_length=100, blank=True, verbose_name='Họ')
    firstname = models.CharField(max_length=100, blank=True, verbose_name='Tên')
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='Tuổi')
    address = models.CharField(max_length=200, blank=True, verbose_name='Địa chỉ công tác')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, verbose_name='Vai trò')
        
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'auth_user'  # Sử dụng tên bảng mặc định của Django User
    
    def get_full_name(self):
        """Lấy tên đầy đủ từ lastname và firstname"""
        if self.lastname and self.firstname:
            return f"{self.lastname} {self.firstname}"
        return super().get_full_name() or self.username

class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

class UserProfile(models.Model):
    """UserProfile giờ chỉ chứa các thông tin bổ sung không có trong CustomUser"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=200, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    followers = models.ManyToManyField(CustomUser, related_name='following', blank=True)
    points = models.IntegerField(default=0)  # Điểm của user
    
    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        return self.user.get_full_name()
    
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

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('upload_file', 'Upload File'),
        ('create_post', 'Create Post'),
        ('like_post', 'Like Post'),
        ('share_post', 'Share Post'),
        ('view_file', 'View File'),
        ('download_file', 'Download File'),
        ('view_free_file', 'View Free File'),
        ('download_free_file', 'Download Free File'),
        ('comment', 'Comment'),
        ('follow', 'Follow User'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Có thể âm (trừ điểm) hoặc dương (cộng điểm)
    description = models.TextField(blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)  # ID của object liên quan (post, file, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.points} points for {self.get_transaction_type_display()}"


class PointSettings(models.Model):
    """Cài đặt điểm cho các hành động"""
    upload_file_points = models.IntegerField(default=20)
    create_post_points = models.IntegerField(default=15)
    like_post_points = models.IntegerField(default=2)
    share_post_points = models.IntegerField(default=5)
    comment_points = models.IntegerField(default=3)
    follow_user_points = models.IntegerField(default=5)
    view_paid_file_cost = models.IntegerField(default=5)
    download_paid_file_cost = models.IntegerField(default=10)
    view_free_file_cost = models.IntegerField(default=1)  # Điểm trừ khi xem tài liệu free
    download_free_file_cost = models.IntegerField(default=5)  # Điểm trừ khi download tài liệu free
    
    class Meta:
        verbose_name = "Point Settings"
        verbose_name_plural = "Point Settings"
    
    def __str__(self):
        return "Point Settings"
    
    @classmethod
    def get_settings(cls):
        """Get or create point settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
