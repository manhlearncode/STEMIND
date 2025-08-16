from django.contrib import admin
from .models import ChatSession, ChatMessage, FileAttachment

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['session_id', 'title', 'user__username']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    ordering = ['-updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__title']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'file_type', 'file_size_display', 'message', 'uploaded_at', 'is_html_file']
    list_filter = ['file_type', 'uploaded_at', 'mime_type']
    search_fields = ['original_name', 'message__content']
    readonly_fields = ['uploaded_at', 'file_size', 'mime_type']
    ordering = ['-uploaded_at']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
    
    def is_html_file(self, obj):
        return obj.is_html()
    is_html_file.boolean = True
    is_html_file.short_description = 'HTML File'
    
    list_display_links = ['original_name']
    list_per_page = 25
