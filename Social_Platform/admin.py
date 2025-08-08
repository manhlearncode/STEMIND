from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Post, Like, Comment, UserProfile, PointTransaction, PointSettings

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'lastname', 'firstname', 'age', 'role', 'address', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'lastname', 'firstname']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('lastname', 'firstname', 'age', 'address', 'role')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin cá nhân', {
            'fields': ('lastname', 'firstname', 'age', 'address', 'role')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'created_at', 'like_count', 'comment_count']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username']
    readonly_fields = ['like_count', 'comment_count']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Nội dung'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__content']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'post__content']
    
    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = 'Nội dung'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'bio_preview', 'followers_count', 'avatar_display']
    search_fields = ['user__username', 'bio']
    readonly_fields = ['followers_count']
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Giới thiệu'
    
    def avatar_display(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "Không có ảnh"
    avatar_display.short_description = 'Ảnh đại diện'

@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'points', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PointSettings)
class PointSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'upload_file_points', 'create_post_points',
        'like_post_points', 'share_post_points', 'comment_points',
        'follow_user_points', 'view_paid_file_cost', 'download_paid_file_cost',
        'view_free_file_cost', 'download_free_file_cost'
    ]
    
    fieldsets = (
        ('Điểm cộng cho hoạt động', {
            'fields': ('upload_file_points', 'create_post_points', 'like_post_points', 
                      'share_post_points', 'comment_points', 'follow_user_points')
        }),
        ('Điểm trừ cho tài liệu có phí', {
            'fields': ('view_paid_file_cost', 'download_paid_file_cost')
        }),
        ('Điểm trừ cho tài liệu free', {
            'fields': ('view_free_file_cost', 'download_free_file_cost')
        }),
    )
    
    def has_add_permission(self, request):
        # Chỉ cho phép 1 instance duy nhất
        return not PointSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa settings
        return False


# Customize admin site
admin.site.site_header = "STEMIND Administration"
admin.site.site_title = "STEMIND Admin Portal"
admin.site.index_title = "Welcome to STEMIND Administration"
