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
        embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.embeddings_model = OpenAIEmbeddings(model=embedding_model_name)

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
            # Files
            files = File.objects.all()
            for file in files:
                if not self._belongs_to_user(file, user_id):
                    continue
                text = self._build_file_text(file)
                if not text:
                    continue
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Posts
            posts = Post.objects.all()
            for post in posts:
                if not self._belongs_to_user(post, user_id):
                    continue
                text = self._build_post_text(post)
                if not text:
                    continue
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Comments
            comments = Comment.objects.all()
            for comment in comments:
                if not self._belongs_to_user(comment, user_id):
                    continue
                text = self._build_comment_text(comment)
                if not text:
                    continue
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
            # Files
            files = File.objects.all()
            for file in files:
                text = self._build_file_text(file)
                if not text:
                    continue
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Posts
            posts = Post.objects.all()
            for post in posts:
                text = self._build_post_text(post)
                if not text:
                    continue
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_openai_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Comments
            comments = Comment.objects.all()
            for comment in comments:
                text = self._build_comment_text(comment)
                if not text:
                    continue
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

    # -------- Helpers để trích xuất nội dung an toàn --------
    def _get_first_attr(self, obj, names):
        for name in names:
            if hasattr(obj, name):
                return getattr(obj, name)
        return None

    def _get_display_name(self, user_obj):
        if not user_obj:
            return ""
        return (
            self._get_first_attr(user_obj, ["username", "email", "name"]) \
            or str(user_obj)
        )

    def _belongs_to_user(self, obj, user_id: str) -> bool:
        owner = self._get_first_attr(obj, ["author", "user", "owner", "created_by"])
        if not owner:
            return False
        owner_id = getattr(owner, "id", None)
        return str(owner_id) == str(user_id)

    def _build_file_text(self, file_obj) -> str:
        title = self._get_first_attr(file_obj, ["title", "name"]) or ""
        description = self._get_first_attr(file_obj, ["file_description", "description", "summary"]) or ""
        category_obj = self._get_first_attr(file_obj, ["category", "categories"])  # có thể None
        if category_obj and isinstance(category_obj, (list, tuple)):
            cat_name = ", ".join([self._get_first_attr(c, ["category_name", "name", "title"]) or str(c) for c in category_obj])
        else:
            cat_name = self._get_first_attr(category_obj, ["category_name", "name", "title"]) if category_obj else ""
        author = self._get_first_attr(file_obj, ["author", "user", "owner", "created_by"]) or None
        author_name = self._get_display_name(author)
        parts = []
        if title:
            parts.append(f"File: {title}")
        if description:
            parts.append(f"Mô tả: {description}")
        if cat_name:
            parts.append(f"Danh mục: {cat_name}")
        if author_name:
            parts.append(f"Tác giả: {author_name}")
        return "\n".join(parts)

    def _build_post_text(self, post_obj) -> str:
        author = self._get_first_attr(post_obj, ["author", "user", "owner", "created_by"]) or None
        author_name = self._get_display_name(author)
        content = self._get_first_attr(post_obj, ["content", "body", "text"]) or ""
        title = self._get_first_attr(post_obj, ["title"]) or ""
        parts = []
        if title:
            parts.append(f"Tiêu đề: {title}")
        if content:
            parts.append(f"Nội dung: {content}")
        if author_name:
            parts.append(f"Tác giả: {author_name}")
        return "\n".join(parts)

    def _build_comment_text(self, comment_obj) -> str:
        user = self._get_first_attr(comment_obj, ["user", "author"]) or None
        user_name = self._get_display_name(user)
        content = self._get_first_attr(comment_obj, ["content", "body", "text"]) or ""
        parts = []
        if content:
            parts.append(f"Comment: {content}")
        if user_name:
            parts.append(f"Người dùng: {user_name}")
        return "\n".join(parts)
    
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
