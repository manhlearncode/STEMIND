from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Like, Comment, UserProfile

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_preview', 'image_preview', 'like_count', 'comment_count', 'created_at']
    list_filter = ['created_at', 'updated_at', 'author']
    search_fields = ['content', 'author__username', 'author__email']
    readonly_fields = ['created_at', 'updated_at', 'like_count', 'comment_count']
    list_select_related = ['author']
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def image_preview(self, obj):
        if obj.image:
            # Sử dụng presigned URL nếu có S3
            try:
                image_url = obj.get_image_presigned_url()
                if image_url:
                    return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', image_url)
                else:
                    return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url)
            except:
                return "No preview"
        return "No image"
    image_preview.short_description = 'Image'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    list_select_related = ['user', 'post']
    list_per_page = 50
    
    def post_preview(self, obj):
        return f"Post #{obj.post.id}: {obj.post.content[:30]}..."
    post_preview.short_description = 'Post'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post_preview', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'post__content']
    readonly_fields = ['created_at']
    list_select_related = ['user', 'post']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def post_preview(self, obj):
        return f"Post #{obj.post.id} by {obj.post.author.username}"
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:40] + "..." if len(obj.content) > 40 else obj.content
    content_preview.short_description = 'Comment'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio_preview', 'avatar_preview', 'followers_count', 'following_count']
    search_fields = ['user__username', 'user__email', 'bio']
    filter_horizontal = ['followers']  # Để dễ quản lý many-to-many relationships
    list_select_related = ['user']
    list_per_page = 20
    
    def bio_preview(self, obj):
        return obj.bio[:50] + "..." if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Bio Preview'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            # Sử dụng presigned URL nếu có S3
            try:
                avatar_url = obj.get_avatar_presigned_url()
                if avatar_url:
                    return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;"/>', avatar_url)
                else:
                    return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;"/>', obj.avatar.url)
            except:
                return "No preview"
        return "No avatar"
    avatar_preview.short_description = 'Avatar'

# Tùy chỉnh admin site header
admin.site.site_header = "Social Platform Admin"
admin.site.site_title = "Social Platform Admin Portal"
admin.site.index_title = "Welcome to Social Platform Administration"
