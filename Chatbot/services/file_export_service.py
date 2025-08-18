import os
import json
import boto3
import re
from datetime import datetime
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class FileExportService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME



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
            # Import html_to_pdf service (giả sử bạn đã có)
            from .html_to_pdf import HTMLToPDFService
            
            pdf_service = HTMLToPDFService()
            pdf_content = pdf_service.convert_url_to_pdf(html_url)
            
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
                pdf_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_path}"
                print(f"✅ Đã lưu PDF lên S3: {pdf_url}")
                
                return pdf_url
            else:
                print("❌ Không thể chuyển đổi HTML thành PDF")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi khi chuyển đổi HTML thành PDF: {e}")
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

