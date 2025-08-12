from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import boto3
from django.core.files.storage import default_storage

class Category(models.Model):
    name = models.CharField(max_length=255, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['name', 'parent']  # Đảm bảo tên unique trong cùng parent

    def __str__(self):
        return self.name
    
    @property
    def is_parent(self):
        """Kiểm tra xem category có phải là parent không"""
        return self.parent is None
    
    @property
    def is_child(self):
        """Kiểm tra xem category có phải là child không"""
        return self.parent is not None
    
    def get_all_children(self):
        """Lấy tất cả children của category này"""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_all_parents(self):
        """Lấy tất cả parents của category này"""
        parents = []
        current = self.parent
        while current:
            parents.append(current)
            current = current.parent
        return parents[::-1]  # Đảo ngược để có thứ tự từ root đến leaf
    
    def get_full_path(self):
        """Lấy đường dẫn đầy đủ của category"""
        path = [self.name]
        current = self.parent
        while current:
            path.append(current.name)
            current = current.parent
        return ' > '.join(reversed(path))
    
class FileExtension(models.Model):
    EXTENSION_TYPES = [
        ('document', 'Văn bản'),
        ('presentation', 'Bài thuyết trình'),
        ('image', 'Ảnh'),
        ('video', 'Video'),
        ('archive', 'Nén'),
        ('other', 'Khác')
    ]
    
    extension_type = models.CharField(max_length=20, choices=EXTENSION_TYPES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.get_extension_type_display()
    
    def get_all_extensions(self):
        return FileExtension.objects.all()
    
    @classmethod
    def get_extension_type_by_file_extension(cls, file_extension):
        """Tự động xác định loại extension dựa trên file extension"""
        extension_mapping = {
            # Documents
            'pdf': 'document',
            'doc': 'document', 
            'docx': 'document',
            'txt': 'document',
            'rtf': 'document',
            'odt': 'document',
            
            # Presentations
            'ppt': 'presentation',
            'pptx': 'presentation',
            'odp': 'presentation',
            
            # Spreadsheets (cũng thuộc documents)
            'xls': 'document',
            'xlsx': 'document',
            'ods': 'document',
            
            # Images
            'jpg': 'image',
            'jpeg': 'image', 
            'png': 'image',
            'gif': 'image',
            'webp': 'image',
            'bmp': 'image',
            'svg': 'image',
            
            # Videos
            'mp4': 'video',
            'avi': 'video',
            'mov': 'video',
            'wmv': 'video',
            'flv': 'video',
            'webm': 'video',
            'mkv': 'video',
            
            # Archives
            'zip': 'archive',
            'rar': 'archive',
            '7z': 'archive',
            'tar': 'archive',
            'gz': 'archive',
        }
        
        return extension_mapping.get(file_extension.lower(), 'other')
    
    @classmethod
    def get_or_create_extension(cls, file_extension):
        """Lấy hoặc tạo extension object dựa trên extension_type"""
        extension_type = cls.get_extension_type_by_file_extension(file_extension)
        
        # Tìm hoặc tạo FileExtension dựa trên extension_type
        extension_obj, created = cls.objects.get_or_create(
            extension_type=extension_type,
            defaults={}
        )
        return extension_obj
    
    
class File(models.Model):
    title = models.CharField(unique=True, max_length=255)
    categories = models.ManyToManyField(Category, related_name='files')
    extension = models.ForeignKey(FileExtension, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    file_thumbnail = models.ImageField(upload_to='thumbnails/%y/%m/%d', blank=True, null=True)
    file_description = models.TextField(blank=True, null=True, max_length=500)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'file']
        ordering = ['-created_at']
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
    
    def __str__(self):
        return f"{self.user.username} - {self.file.title}"

