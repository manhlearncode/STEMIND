import os
import json
import django
from django.conf import settings
from django.core.management.base import BaseCommand
from File_sharing_platform.models import File, Category
from Social_Platform.models import Post, Comment
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Chalk.settings')
django.setup()

class Command(BaseCommand):
    help = 'Train chatbot với dữ liệu từ database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='embeddings.json',
            help='Tên file JSON output'
        )

    def handle(self, *args, **options):
        # Load environment variables
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        output_file = options['output']
        
        # Thu thập dữ liệu từ database
        training_data = self.collect_training_data()
        
        # Tạo embeddings
        self.create_embeddings(training_data, output_file)
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã train chatbot thành công! File: {output_file}')
        )

    def collect_training_data(self):
        """Thu thập dữ liệu từ các model"""
        training_data = []
        
        # Lấy dữ liệu từ File sharing platform
        try:
            files = File.objects.all()
            self.stdout.write(f"Tìm thấy {files.count()} files")
            for file in files:
                text = f"File: {file.title}\n"
                if file.file_description:
                    text += f"Mô tả: {file.file_description}\n"
                text += f"Danh mục: {file.category.category_name}\n"
                text += f"Tác giả: {file.author.username}\n"
                text += f"Trạng thái: {'Miễn phí' if file.file_status == 0 else 'Có phí'}\n"
                if file.file_price > 0:
                    text += f"Giá: {file.file_price}\n"
                training_data.append(text)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Lỗi khi lấy dữ liệu files: {e}")
            )
        
        # Lấy dữ liệu từ Social platform
        try:
            posts = Post.objects.all()
            self.stdout.write(f"Tìm thấy {posts.count()} posts")
            for post in posts:
                text = f"Post từ {post.author.username}: {post.content}\n"
                text += f"Thời gian: {post.created_at}\n"
                training_data.append(text)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Lỗi khi lấy dữ liệu posts: {e}")
            )
        
        # Lấy comments
        try:
            comments = Comment.objects.all()
            self.stdout.write(f"Tìm thấy {comments.count()} comments")
            for comment in comments:
                text = f"Comment từ {comment.user.username}: {comment.content}\n"
                text += f"Thời gian: {comment.created_at}\n"
                training_data.append(text)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Lỗi khi lấy dữ liệu comments: {e}")
            )
        
        # Lấy categories
        try:
            categories = Category.objects.all()
            self.stdout.write(f"Tìm thấy {categories.count()} categories")
            for category in categories:
                text = f"Danh mục: {category.category_name}\n"
                training_data.append(text)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Lỗi khi lấy dữ liệu categories: {e}")
            )
        
        # Thêm dữ liệu mẫu nếu database trống
        if not training_data:
            self.stdout.write(
                self.style.WARNING("Database trống, thêm dữ liệu mẫu...")
            )
            training_data = [
                "STEM Education là phương pháp giáo dục tích hợp Science, Technology, Engineering và Mathematics",
                "Python là ngôn ngữ lập trình phổ biến cho người mới bắt đầu",
                "Machine Learning là một nhánh của Artificial Intelligence",
                "Toán học là nền tảng của tất cả các ngành khoa học",
                "Công nghệ đang thay đổi cách chúng ta học tập và làm việc"
            ]
        
        self.stdout.write(f"Tổng cộng {len(training_data)} mẫu dữ liệu để train")
        return training_data

    def chunk_text(self, text, max_chunk_size=500):
        """Chia text thành các chunk nhỏ"""
        words = text.split()
        chunks = []
        current_chunk = []
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= max_chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def create_embedding(self, text):
        """Tạo embedding cho text"""
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return embeddings.embed_query(text)

    def create_embeddings(self, training_data, output_file):
        """Tạo embeddings cho tất cả dữ liệu training"""
        all_chunks = []
        all_embeddings = []
        
        for text in training_data:
            if not text.strip():
                continue
                
            chunks = self.chunk_text(text)
            for chunk in chunks:
                try:
                    embedding = self.create_embedding(chunk)
                    all_chunks.append(chunk)
                    all_embeddings.append(embedding)
                    self.stdout.write(f"Đã tạo embedding cho chunk: {chunk[:100]}...")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Lỗi khi tạo embedding: {e}")
                    )
        
        # Lưu vào JSON
        data = {
            'chunks': all_chunks,
            'embeddings': all_embeddings
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        self.stdout.write(f"Đã lưu {len(all_chunks)} chunks và embeddings") 