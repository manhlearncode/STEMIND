from django.contrib import admin
from .models import Category, File, Favorite, FileExtension
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'parent')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_parent(self, obj):
        return obj.is_parent
    is_parent.boolean = True
    is_parent.short_description = "Là category cha"

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['title', 'categories_display', 'author', 'thumbnail_preview', 'file_status', 'file_downloads', 'created_at']
    list_filter = ['file_status', 'categories', 'created_at']
    search_fields = ['title', 'file_description']
    readonly_fields = ['file_downloads', 'created_at', 'updated_at', 'thumbnail_preview']
    filter_horizontal = ['categories']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('title', 'categories', 'author')
        }),
        ('Nội dung', {
            'fields': ('file_description', 'file_urls', 'file_thumbnail', 'thumbnail_preview')
        }),
        ('Trạng thái', {
            'fields': ('file_status', 'file_price', 'file_downloads')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def categories_display(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    categories_display.short_description = "Categories"
    
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

@admin.register(FileExtension)
class FileExtensionAdmin(admin.ModelAdmin):
    list_display = ['extension_type', 'created_at', 'updated_at']
    search_fields = ['extension']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('extension_type',)
        }),
    )

