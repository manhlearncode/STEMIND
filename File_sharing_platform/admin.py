from django.contrib import admin
from .models import Category, File, Favorite
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'created_at', 'updated_at']
    search_fields = ['category_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'thumbnail_preview', 'file_status', 'file_downloads', 'created_at']
    list_filter = ['file_status', 'category', 'created_at']
    search_fields = ['title', 'file_description']
    readonly_fields = ['file_downloads', 'created_at', 'updated_at', 'thumbnail_preview']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'category', 'author')
        }),
        ('Nội dung', {
            'fields': ('file_description', 'file_urls', 'file_thumbnail', 'thumbnail_preview')
        }),
        ('Trạng thái', {
            'fields': ('file_status', 'file_downloads')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def thumbnail_preview(self, obj):
        if obj.file_thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.file_thumbnail.url
            )
        return "Chưa có thumbnail"
    thumbnail_preview.short_description = "Thumbnail Preview"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'file__title']
    readonly_fields = ['created_at']

