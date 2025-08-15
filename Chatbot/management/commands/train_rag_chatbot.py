import os
import json
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import openai
from langchain_openai import OpenAIEmbeddings
from django.core.management.base import BaseCommand
from django.conf import settings
from File_sharing_platform.models import File, Category
from Social_Platform.models import Post, Comment
from datetime import datetime

# Import service từ Chatbot app
from Chatbot.services.rag_chatbot_service import RAGChatbotService
from Chatbot.services.user_embedding_service import UserEmbeddingService

class Command(BaseCommand):
    help = 'Train RAG chatbot by creating embeddings from database data using Chatbot services'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='Specific user ID to create personal embeddings for',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Create embeddings for all users',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=500,
            help='Size of text chunks (default: 500)',
        )
        parser.add_argument(
            '--embeddings-file',
            type=str,
            default='stem_embeddings.json',
            help='Output file for embeddings (default: stem_embeddings.json)',
        )
    
    def handle(self, *args, **options):
        load_dotenv()
        
        user_id = options.get('user_id')
        all_users = options.get('all_users')
        chunk_size = options.get('chunk_size')
        embeddings_file = options.get('embeddings_file')
        
        # Khởi tạo service từ Chatbot app
        self.rag_service = RAGChatbotService(embeddings_file)
        self.user_service = UserEmbeddingService()

        # Khởi tạo OpenAI embeddings (chỉ 1 lần)
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

        if all_users:
            self.stdout.write("Tạo embeddings cho tất cả users...")
            self.create_embeddings_for_all_users(chunk_size)
        elif user_id:
            self.stdout.write(f"Tạo embeddings cá nhân cho user {user_id}...")
            self.create_user_embeddings(user_id, chunk_size)
            self.stdout.write(
                self.style.SUCCESS(f'Đã tạo embeddings cá nhân cho user {user_id}')
            )
        else:
            self.stdout.write("Tạo embeddings chung từ database...")
            self.create_global_embeddings(chunk_size, embeddings_file)
            self.stdout.write(
                self.style.SUCCESS(f'Đã tạo embeddings và lưu vào {embeddings_file}')
            )
    
    def create_embeddings_for_all_users(self, chunk_size):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        users = User.objects.all()
        total_users = users.count()
        
        for i, user in enumerate(users, 1):
            self.stdout.write(f"Đang xử lý user {i}/{total_users}: {user.username} (ID: {user.id})")
            try:
                self.create_user_embeddings(str(user.id), chunk_size)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Hoàn thành user {user.username}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Lỗi với user {user.username}: {e}')
                )
    
    def create_user_embeddings(self, user_id, chunk_size):
        all_chunks = []
        all_embeddings = []
        
        try:
            files = File.objects.filter(author__id=user_id)
            for file in files:
                text = f"File: {file.title}\n"
                if file.file_description:
                    text += f"Mô tả: {file.file_description}\n"
                text += f"Danh mục: {file.category.category_name}\n"
                text += f"Tác giả: {file.author.username}\n"
                
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            posts = Post.objects.filter(author__id=user_id)
            for post in posts:
                text = f"Post từ {post.author.username}: {post.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            comments = Comment.objects.filter(user__id=user_id)
            for comment in comments:
                text = f"Comment từ {comment.user.username}: {comment.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            if all_chunks and all_embeddings:
                data = {
                    'user_id': user_id,
                    'chunks': all_chunks,
                    'embeddings': all_embeddings,
                    'total_chunks': len(all_chunks),
                    'created_at': str(datetime.now())
                }
                
                filename = f"user_{user_id}_embeddings.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.stdout.write(f"Đã tạo {len(all_chunks)} chunks cho user {user_id} -> {filename}")
            else:
                self.stdout.write(f"Không có dữ liệu cho user {user_id}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Lỗi khi tạo embeddings cho user {user_id}: {e}"))
    
    def create_global_embeddings(self, chunk_size, embeddings_file):
        all_chunks = []
        all_embeddings = []
        
        try:
            files = File.objects.all()
            for file in files:
                text = f"File: {file.title}\n"
                if file.file_description:
                    text += f"Mô tả: {file.file_description}\n"
                text += f"Danh mục: {file.category.category_name}\n"
                text += f"Tác giả: {file.author.username}\n"
                
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            posts = Post.objects.all()
            for post in posts:
                text = f"Post từ {post.author.username}: {post.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            comments = Comment.objects.all()
            for comment in comments:
                text = f"Comment từ {comment.user.username}: {comment.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            if all_chunks and all_embeddings:
                data = {
                    'chunks': all_chunks,
                    'embeddings': all_embeddings
                }
                with open(embeddings_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.stdout.write(f"Đã tạo và lưu {len(all_chunks)} chunks vào {embeddings_file}")
            else:
                self.stdout.write(self.style.WARNING("Không có dữ liệu để tạo embeddings"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Lỗi khi tạo embeddings từ database: {e}"))
    
    def chunk_text(self, text, max_chunk_size=500):
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
    
    def get_openai_embedding(self, text):
        try:
            return self.embeddings_model.embed_query(text)
        except Exception as e:
            self.stdout.write(f"Lỗi khi tạo embedding OpenAI: {e}")
            return None
