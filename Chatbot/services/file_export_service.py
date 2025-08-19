import os
import json
import boto3
import re
from datetime import datetime
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from typing import Optional

class FileExportService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def create_html_content(self, content: str, title: str = "STEMIND Document") -> str:
        """Tạo nội dung HTML hoàn chỉnh từ content text"""
        html_template = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }}
        h1 {{
            color: #006065;
            border-bottom: 2px solid #006065;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #007a82;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h3 {{
            color: #00897B;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        ul, ol {{
            margin-bottom: 15px;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #006065;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        @media print {{
            body {{ margin: 0; padding: 15px; }}
            .content {{ background: white; border: 1px solid #ddd; }}
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="content">
        {content.replace(chr(10), '<br>').replace(chr(13), '')}
    </div>
    <div class="footer">
        <p>Được tạo bởi STEMIND AI Assistant - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
    </div>
</body>
</html>
        """
        return html_template

    def convert_html_to_pdf_content(self, html_content: str, pdf_filename: str) -> Optional[bytes]:
        """Convert HTML content trực tiếp thành PDF bytes (không lưu lên S3)"""
        try:
            # Import html_to_pdf service
            from .html_to_pdf import HTMLToPDFService
            
            pdf_service = HTMLToPDFService()
            
            # Convert trực tiếp từ HTML string thành PDF bytes
            pdf_content = pdf_service.convert_html_string_to_pdf(html_content)
            
            if pdf_content:
                print(f"✅ Đã convert HTML thành PDF: {len(pdf_content)} bytes")
                return pdf_content
            else:
                print("❌ Không thể convert HTML thành PDF")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi khi convert HTML thành PDF: {e}")
            return None

    def save_html_to_s3(self, html_content: str, filename: str) -> str:
        """Lưu file HTML lên AWS S3"""
        try:
            # Tạo đường dẫn cho file HTML
            html_filename = filename.replace('.pdf', '.html')
            s3_path = f"media/chatbot_exports/{html_filename}"
            
            # Upload lên S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_path,
                Body=html_content.encode('utf-8'),
                ContentType='text/html',
                ACL='public-read'
            )
            
            # Trả về URL của file HTML
            html_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_path}"
            print(f"✅ Đã lưu HTML lên S3: {html_url}")
            
            return html_url
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu HTML lên S3: {e}")
            return None

    def convert_html_to_pdf(self, html_url: str, pdf_filename: str) -> str:
        """Chuyển đổi HTML thành PDF bằng html_to_pdf service"""
        try:
            # Import html_to_pdf service
            from .html_to_pdf import HTMLToPDFService
            
            pdf_service = HTMLToPDFService()
            
            # Sử dụng convert_html_string_to_pdf thay vì convert_url_to_pdf để tránh vấn đề S3
            # Đọc HTML content từ S3 trước
            html_content = self._get_html_content_from_s3(html_url)
            if not html_content:
                raise Exception("Không thể đọc HTML content từ S3")
            
            # Convert trực tiếp từ HTML string
            pdf_content = pdf_service.convert_html_string_to_pdf(html_content)
            
            if pdf_content:
                # Lưu PDF lên S3
                s3_path = f"media/chatbot_exports/{pdf_filename}"
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_path,
                    Body=pdf_content,
                    ContentType='application/pdf',
                    ACL='public-read'
                )
                
                # Trả về URL của file PDF
                pdf_url = f"https://{self.bucket_name}.s3.amazonaws.com/{pdf_url}"
                print(f"✅ Đã lưu PDF lên S3: {pdf_url}")
                
                return pdf_url
            else:
                print("❌ Không thể chuyển đổi HTML thành PDF")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi khi chuyển đổi HTML thành PDF: {e}")
            return None

    def _get_html_content_from_s3(self, html_url: str) -> str:
        """Lấy HTML content từ S3 URL"""
        try:
            # Extract key từ URL
            key = html_url.split('.com/')[-1]
            
            # Download content từ S3
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            html_content = response['Body'].read().decode('utf-8')
            
            return html_content
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc HTML từ S3: {e}")
            return None

    def export_to_pdf(self, content: str, filename: str, title: str = "STEMIND Document") -> str:
        """
        Xuất nội dung thành PDF thông qua HTML
        Returns: URL của file PDF trên S3
        """
        try:
            print(f"🔄 Bắt đầu xuất file: {filename}")
            
            # 1. Tạo nội dung HTML
            html_content = self.create_html_content(content, title)
            print("✅ Đã tạo nội dung HTML")
            
            # 2. Lưu HTML lên S3
            html_url = self.save_html_to_s3(html_content, filename)
            if not html_url:
                raise Exception("Không thể lưu HTML lên S3")
            
            # 3. Chuyển đổi HTML thành PDF
            pdf_url = self.convert_html_to_pdf(html_url, filename)
            if not pdf_url:
                raise Exception("Không thể chuyển đổi HTML thành PDF")
            
            print(f"🎉 Hoàn thành xuất file: {pdf_url}")
            return pdf_url
            
        except Exception as e:
            print(f"❌ Lỗi trong quá trình xuất file: {e}")
            return None

    def cleanup_temp_files(self, html_url: str = None):
        """Dọn dẹp file tạm (tùy chọn)"""
        try:
            if html_url:
                # Xóa file HTML tạm nếu cần
                html_key = html_url.split('.com/')[-1]
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=html_key
                )
                print("✅ Đã xóa file HTML tạm")
        except Exception as e:
            print(f"⚠️ Không thể xóa file tạm: {e}")

