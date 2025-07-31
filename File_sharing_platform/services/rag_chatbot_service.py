import os
import json
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Chalk.settings')
django.setup()

from File_sharing_platform.models import File, Category
from Social_Platform.models import Post, Comment

class RAGChatbotService:
    def __init__(self, embeddings_file='stem_embeddings.json'):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.embeddings_file = embeddings_file
        self.chunks = []
        self.embeddings = []
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load embeddings từ file JSON"""
        if os.path.exists(self.embeddings_file):
            try:
                with open(self.embeddings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', [])
                    self.embeddings = np.array(data.get('embeddings', []))
                print(f"Đã load {len(self.chunks)} chunks từ {self.embeddings_file}")
            except Exception as e:
                print(f"Lỗi khi load embeddings: {e}")
                self.chunks = []
                self.embeddings = []
        else:
            print(f"File embeddings không tồn tại: {self.embeddings_file}")
            # Tự động tạo embeddings từ database
            self.create_embeddings_from_database()
    
    def get_gemini_embedding(self, text):
        """Tạo embedding cho text sử dụng Gemini"""
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            print(f"Lỗi khi tạo embedding: {e}")
            return None
    
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
    
    def create_embeddings_from_database(self):
        """Tạo embeddings từ dữ liệu database"""
        print("Tạo embeddings từ database...")
        all_chunks = []
        all_embeddings = []
        
        try:
            # Lấy dữ liệu từ File sharing platform
            files = File.objects.all()
            for file in files:
                text = f"File: {file.title}\n"
                if file.file_description:
                    text += f"Mô tả: {file.file_description}\n"
                text += f"Danh mục: {file.category.category_name}\n"
                text += f"Tác giả: {file.author.username}\n"
                
                chunks = self.chunk_text(text)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Lấy dữ liệu từ Social platform
            posts = Post.objects.all()
            for post in posts:
                text = f"Post từ {post.author.username}: {post.content}\n"
                chunks = self.chunk_text(text)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Lấy comments
            comments = Comment.objects.all()
            for comment in comments:
                text = f"Comment từ {comment.user.username}: {comment.content}\n"
                chunks = self.chunk_text(text)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            

            
            if all_chunks and all_embeddings:
                # Lưu vào file
                data = {
                    'chunks': all_chunks,
                    'embeddings': all_embeddings
                }
                with open(self.embeddings_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Cập nhật instance variables
                self.chunks = all_chunks
                self.embeddings = np.array(all_embeddings)
                
                print(f"Đã tạo và lưu {len(all_chunks)} chunks vào {self.embeddings_file}")
            else:
                print("Không có dữ liệu để tạo embeddings")
                
        except Exception as e:
            print(f"Lỗi khi tạo embeddings từ database: {e}")
    
    def answer_question(self, query, top_k=3):
        """Trả lời câu hỏi sử dụng RAG với fallback đến Gemini"""
        if not self.chunks or len(self.embeddings) == 0:
            # Fallback trực tiếp đến Gemini nếu không có embeddings
            return self._fallback_to_gemini(query)
        
        try:
            # Tạo embedding cho câu hỏi
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return self._fallback_to_gemini(query)
            
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Tính cosine similarity
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            top_chunks = [self.chunks[i] for i in top_indices]
            top_scores = [similarities[i] for i in top_indices]
            
            # Kiểm tra xem có thông tin liên quan không (similarity > 0.3)
            relevant_chunks = []
            for i, score in enumerate(top_scores):
                if score > 0.3:  # Ngưỡng similarity
                    relevant_chunks.append(top_chunks[i])
            
            if relevant_chunks:
                # Có thông tin liên quan, sử dụng RAG
                context = "\n".join(relevant_chunks)
                prompt = f"""Dựa trên các đoạn tài liệu sau, hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và chính xác.

Tài liệu liên quan:
{context}

Câu hỏi: {query}

Hãy trả lời bằng tiếng Việt, sử dụng thông tin từ tài liệu trên.

Trả lời:"""

                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(prompt)
                return response.text
            else:
                # Không có thông tin liên quan, fallback đến Gemini
                return self._fallback_to_gemini(query)
            
        except Exception as e:
            print(f"Lỗi trong RAG: {e}")
            return self._fallback_to_gemini(query)
    
    def _fallback_to_gemini(self, query):
        """Fallback trực tiếp đến Gemini API"""
        try:
            prompt = f"""Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi sau một cách chi tiết, dễ hiểu và chính xác bằng tiếng Việt:

Câu hỏi: {query}

Trả lời:"""

            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi: {str(e)}"
    
    def get_similar_chunks(self, query, top_k=5):
        """Tìm các chunk tương tự với câu hỏi"""
        if not self.chunks or len(self.embeddings) == 0:
            return []
        
        try:
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return []
            
            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            similar_chunks = []
            for i in top_indices:
                similar_chunks.append({
                    'chunk': self.chunks[i],
                    'similarity': similarities[i],
                    'preview': self.chunks[i][:200] + '...' if len(self.chunks[i]) > 200 else self.chunks[i]
                })
            
            return similar_chunks
            
        except Exception as e:
            print(f"Lỗi khi tìm chunks tương tự: {e}")
            return []

# Global instance
rag_chatbot_service = None

def get_rag_chatbot_service():
    """Get global RAG chatbot service instance"""
    global rag_chatbot_service
    if rag_chatbot_service is None:
        try:
            rag_chatbot_service = RAGChatbotService()
        except Exception as e:
            print(f"Lỗi khi khởi tạo RAG chatbot service: {e}")
            return None
    return rag_chatbot_service