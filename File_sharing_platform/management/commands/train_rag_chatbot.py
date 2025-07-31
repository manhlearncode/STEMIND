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
    help = 'Train RAG chatbot với dữ liệu từ database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='stem_embeddings.json',
            help='Tên file JSON output'
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=500,
            help='Kích thước chunk tối đa'
        )

    def handle(self, *args, **options):
        # Load environment variables
        load_dotenv()
        
        # Kiểm tra API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.stdout.write(
                self.style.ERROR("GOOGLE_API_KEY không được tìm thấy trong file .env")
            )
            return
        
        self.stdout.write(f"Đã tìm thấy API key: {api_key[:10]}...")
        
        genai.configure(api_key=api_key)
        
        output_file = options['output']
        chunk_size = options['chunk_size']
        
        # Thu thập dữ liệu từ database
        training_data = self.collect_training_data()
        
        # Tạo embeddings
        self.create_embeddings(training_data, output_file, chunk_size)
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã train RAG chatbot thành công! File: {output_file}')
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
        
        # Kiểm tra nếu database trống
        if not training_data:
            self.stdout.write(
                self.style.WARNING("Database trống, không có dữ liệu để train.")
            )
            return []
        
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

    def get_gemini_embedding(self, text):
        """Tạo embedding cho text"""
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Lỗi khi tạo embedding: {e}")
            )
            return None

    def create_embeddings(self, training_data, output_file, chunk_size):
        """Tạo embeddings cho tất cả dữ liệu training"""
        all_chunks = []
        all_embeddings = []
        
        total_texts = len(training_data)
        processed = 0
        
        for text in training_data:
            if not text.strip():
                continue
                
            chunks = self.chunk_text(text, chunk_size)
            for chunk in chunks:
                try:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
                        self.stdout.write(f"✅ Đã tạo embedding cho chunk: {chunk[:100]}...")
                    else:
                        self.stdout.write(f"❌ Không thể tạo embedding cho chunk: {chunk[:100]}...")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Lỗi khi tạo embedding: {e}")
                    )
                    continue
            
            processed += 1
            progress = (processed / total_texts) * 100
            self.stdout.write(f"Tiến độ: {progress:.1f}% ({processed}/{total_texts})")
        
        # Chỉ lưu nếu có dữ liệu
        if all_chunks and all_embeddings:
            # Lưu vào JSON
            data = {
                'chunks': all_chunks,
                'embeddings': all_embeddings,
                'metadata': {
                    'total_chunks': len(all_chunks),
                    'chunk_size': chunk_size,
                    'model': 'models/embedding-001',
                    'created_at': str(django.utils.timezone.now())
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Đã lưu {len(all_chunks)} chunks và embeddings vào {output_file}")
            )
            
            # Hiển thị thống kê
            self.stdout.write("\n" + "="*50)
            self.stdout.write("📊 THỐNG KÊ:")
            self.stdout.write(f"• Tổng số văn bản gốc: {total_texts}")
            self.stdout.write(f"• Tổng số chunks: {len(all_chunks)}")
            self.stdout.write(f"• Kích thước chunk tối đa: {chunk_size} từ")
            self.stdout.write(f"• Model embedding: models/embedding-001")
            self.stdout.write(f"• File output: {output_file}")
            self.stdout.write("="*50)
            
        else:
            self.stdout.write(
                self.style.ERROR("❌ Không có dữ liệu nào được tạo thành công")
            )