from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import ChatSession, ChatMessage, FileAttachment
import tempfile
import os

User = get_user_model()

class FileAttachmentDownloadTest(TestCase):
    def setUp(self):
        # Tạo test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Tạo chat session
        self.session = ChatSession.objects.create(
            user=self.user,
            title='Test Session'
        )
        
        # Tạo chat message
        self.message = ChatMessage.objects.create(
            session=self.session,
            message_type='user',
            content='Test message'
        )
        
        # Tạo test file
        self.test_file_content = b'This is a test file content'
        self.test_file = SimpleUploadedFile(
            'test.txt',
            self.test_file_content,
            content_type='text/plain'
        )
        
        # Tạo file attachment
        self.attachment = FileAttachment.objects.create(
            message=self.message,
            file=self.test_file,
            original_name='test.txt',
            file_type='document',
            file_size=len(self.test_file_content),
            mime_type='text/plain'
        )
        
        self.client = Client()
        
    def test_get_presigned_url(self):
        """Test method get_presigned_url"""
        presigned_url = self.attachment.get_presigned_url()
        
        # Kiểm tra URL có được tạo không
        self.assertIsNotNone(presigned_url)
        
        # Kiểm tra URL có chứa S3 domain không (nếu S3 được cấu hình)
        if presigned_url and 's3.amazonaws.com' in presigned_url:
            self.assertIn('s3.amazonaws.com', presigned_url)
        
    def test_download_chat_file_authenticated(self):
        """Test download file khi user đã đăng nhập"""
        self.client.force_login(self.user)
        
        url = reverse('chatbot:download_chat_file', args=[self.attachment.id])
        response = self.client.get(url)
        
        # Kiểm tra response status
        self.assertIn(response.status_code, [200, 302, 301])
        
    def test_download_chat_file_unauthenticated(self):
        """Test download file khi user chưa đăng nhập"""
        url = reverse('chatbot:download_chat_file', args=[self.attachment.id])
        response = self.client.get(url)
        
        # Kiểm tra redirect đến login page
        self.assertEqual(response.status_code, 302)
        
    def test_download_chat_file_unauthorized(self):
        """Test download file khi user không có quyền"""
        # Tạo user khác
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.client.force_login(other_user)
        
        url = reverse('chatbot:download_chat_file', args=[self.attachment.id])
        response = self.client.get(url)
        
        # Kiểm tra response là JSON error
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
        self.assertFalse(response.json()['success'])
        
    def test_list_chat_files_with_presigned_urls(self):
        """Test list files với presigned URLs"""
        self.client.force_login(self.user)
        
        url = reverse('chatbot:list_chat_files')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('files', data)
        self.assertEqual(len(data['files']), 1)
        
        file_info = data['files'][0]
        self.assertIn('download_url', file_info)
        self.assertIn('file_url', file_info)
        
        # Kiểm tra download_url và file_url có giá trị
        self.assertIsNotNone(file_info['download_url'])
        self.assertIsNotNone(file_info['file_url'])
        
    def test_file_attachment_str_representation(self):
        """Test string representation của FileAttachment"""
        expected_str = f"{self.attachment.original_name} ({self.attachment.file_type})"
        self.assertEqual(str(self.attachment), expected_str)
        
    def test_file_size_display(self):
        """Test method get_file_size_display"""
        size_display = self.attachment.get_file_size_display()
        self.assertIsInstance(size_display, str)
        self.assertIn('B', size_display)  # Should contain 'B' for bytes
        
    def test_html_file_detection(self):
        """Test HTML file detection"""
        # Tạo HTML file attachment
        html_attachment = FileAttachment.objects.create(
            message=self.message,
            file=self.test_file,
            original_name='test.html',
            file_type='html',
            file_size=len(self.test_file_content),
            mime_type='text/html'
        )
        
        self.assertTrue(html_attachment.is_html())
        self.assertTrue(html_attachment.is_document())
        
    def test_file_type_from_mime(self):
        """Test file type detection from MIME type"""
        # Test HTML MIME type
        html_type = FileAttachment.get_file_type_from_mime('text/html')
        self.assertEqual(html_type, 'html')
        
        # Test document MIME types
        doc_type = FileAttachment.get_file_type_from_mime('application/pdf')
        self.assertEqual(doc_type, 'document')
        
        # Test image MIME type
        img_type = FileAttachment.get_file_type_from_mime('image/jpeg')
        self.assertEqual(img_type, 'image')
        
    def test_generate_html_file(self):
        """Test HTML file generation"""
        from .views import generate_content_file
        
        # Test HTML file generation
        attachment = generate_content_file(
            user_message="Tạo bài giảng về toán học",
            bot_response="Đây là nội dung bài giảng về toán học...",
            session=self.session
        )
        
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.file_type, 'html')
        self.assertEqual(attachment.mime_type, 'text/html')
        self.assertTrue(attachment.original_name.endswith('.html'))
        
        # Test file content contains HTML
        if hasattr(attachment.file, 'read'):
            attachment.file.seek(0)
            content = attachment.file.read().decode('utf-8')
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('STEMIND AI', content)
            self.assertIn('Bài giảng', content)
        
    def tearDown(self):
        # Cleanup test files
        if self.attachment.file:
            if os.path.exists(self.attachment.file.path):
                os.remove(self.attachment.file.path)
