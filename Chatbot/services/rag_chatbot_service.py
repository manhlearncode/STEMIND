import os
import json
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import asyncio
import threading
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .user_embedding_service import UserEmbeddingService

load_dotenv()

class UserEmbeddingService:
    def __init__(self):
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    def load_user_embeddings(self, user_id: str) -> Tuple[List[str], np.ndarray]:
        """
        Load embeddings của user cụ thể từ file JSON
        Returns: (chunks, embeddings)
        """
        filename = f"user_{user_id}_embeddings.json"

        if not os.path.exists(filename):
            print(f"File {filename} không tồn tại")
            return [], np.array([])
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chunks = data.get('chunks', [])
                embeddings = np.array(data.get('embeddings', []))
                print(f"Đã load {len(chunks)} chunks cho user {user_id}")
                return chunks, embeddings
        except Exception as e:
            print(f"Lỗi khi load embeddings cho user {user_id}: {e}")
            return [], np.array([])
    
    def get_user_context(self, user_id: str, query: str, top_k: int = 3) -> List[str]:
        """
        Lấy context liên quan từ dữ liệu của user
        """
        chunks, embeddings = self.load_user_embeddings(user_id)
        
        if len(chunks) == 0 or len(embeddings) == 0:
            return []
        
        try:
            # Tạo embedding cho câu hỏi
            query_embedding = self.embeddings_model.embed_query(query)
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Tính similarity
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Giảm ngưỡng similarity để lấy nhiều context hơn
            relevant_chunks = []
            for i in top_indices:
                if similarities[i] > 0.1:  # Giảm từ 0.3 xuống 0.1
                    relevant_chunks.append(chunks[i])
            
            return relevant_chunks
            
        except Exception as e:
            print(f"Lỗi khi tìm context cho user {user_id}: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[dict]:
        """
        Lấy thông tin profile của user từ file JSON
        """
        filename = f"user_{user_id}_embeddings.json"
        
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'user_id': data.get('user_id'),
                    'total_chunks': data.get('total_chunks', 0),
                    'created_at': data.get('created_at'),
                    'has_data': len(data.get('chunks', [])) > 0
                }
        except Exception as e:
            print(f"Lỗi khi load profile cho user {user_id}: {e}")
            return None
    
    def list_all_users(self) -> List[str]:
        """
        Liệt kê tất cả users có file embeddings
        """
        users = []
        for filename in os.listdir('.'):
            if filename.startswith('user_') and filename.endswith('_embeddings.json'):
                user_id = filename.replace('user_', '').replace('_embeddings.json', '')
                users.append(user_id)
        return users

import os
import json
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .user_embedding_service import UserEmbeddingService

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
        self.user_embedding_service = UserEmbeddingService()
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
    
    def get_gemini_embedding(self, text):
        """Tạo embedding cho text sử dụng Gemini"""
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            print(f"Lỗi khi tạo embedding: {e}")
            return None
        
    def _safe_generate_content(self, model, prompt):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(loop.run_in_executor(None, model.generate_content, prompt))
    
    def answer_question_with_user_context(self, query: str, user_id: str, top_k: int = 3):
        """
        Trả lời câu hỏi sử dụng cả dữ liệu chung và dữ liệu cá nhân của user
        """
        try:
            # Lấy context từ dữ liệu cá nhân của user
            user_chunks = self.user_embedding_service.get_user_context(user_id, query, top_k)
            
            # Lấy context từ dữ liệu chung
            global_chunks = self.get_global_context(query, top_k)
            
            # Kết hợp context
            all_chunks = user_chunks + global_chunks
            
            if all_chunks:
                # Có thông tin liên quan, sử dụng RAG + Gemini
                context = "\n".join(all_chunks)
                prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Dựa trên các đoạn tài liệu sau (bao gồm cả dữ liệu cá nhân của người dùng và dữ liệu chung), hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và chính xác.

Tài liệu liên quan:
{context}

Câu hỏi: {query}

Hãy trả lời bằng tiếng Việt, ưu tiên sử dụng thông tin từ tài liệu cá nhân của người dùng nếu có. Nếu cần, bạn có thể bổ sung kiến thức tổng quát của mình để giải thích rõ hơn.

Trả lời:"""
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = self._safe_generate_content(model, prompt)
                return response.text
            else:
                # Không có thông tin liên quan, sử dụng Gemini AI với prompt thông minh
                return self._smart_fallback_to_gemini(query)
            
        except Exception as e:
            print(f"Lỗi trong RAG với user context: {e}")
            return self._smart_fallback_to_gemini(query)
    
    def answer_question(self, query, top_k=3):
        """Trả lời câu hỏi sử dụng RAG với fallback đến Gemini"""
        try:
            # Tạo embedding cho câu hỏi
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return self._smart_fallback_to_gemini(query)
            
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Tính cosine similarity
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            top_chunks = [self.chunks[i] for i in top_indices]
            top_scores = [similarities[i] for i in top_indices]
            
            # Giảm ngưỡng similarity để lấy nhiều context hơn
            relevant_chunks = []
            for i, score in enumerate(top_scores):
                if score > 0.1:  # Giảm từ 0.3 xuống 0.1
                    relevant_chunks.append(top_chunks[i])
            
            if relevant_chunks:
                # Có thông tin liên quan, sử dụng RAG + Gemini
                context = "\n".join(relevant_chunks)
                prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Dựa trên các đoạn tài liệu sau, hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và chính xác.

Tài liệu liên quan:
{context}

Câu hỏi: {query}

Hãy trả lời bằng tiếng Việt, sử dụng thông tin từ tài liệu trên. Nếu cần, bạn có thể bổ sung kiến thức tổng quát của mình để giải thích rõ hơn.

Trả lời:"""
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = self._safe_generate_content(model, prompt)
                return response.text
            else:
                # Không có thông tin liên quan, sử dụng Gemini AI với prompt thông minh
                return self._smart_fallback_to_gemini(query)
            
        except Exception as e:
            print(f"Lỗi trong RAG: {e}")
            return self._smart_fallback_to_gemini(query)
    
    def get_global_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Lấy context từ dữ liệu chung
        """
        if not self.chunks or len(self.embeddings) == 0:
            return []
        
        try:
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return []
            
            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            relevant_chunks = []
            for i in top_indices:
                if similarities[i] > 0.1:  # Giảm ngưỡng similarity
                    relevant_chunks.append(self.chunks[i])
            
            return relevant_chunks
            
        except Exception as e:
            print(f"Lỗi khi lấy global context: {e}")
            return []
    
    def _smart_fallback_to_gemini(self, query):
        """Fallback thông minh đến Gemini API với prompt phù hợp"""
        try:
            # Phân tích loại câu hỏi để tạo prompt phù hợp
            if any(word in query.lower() for word in ['xin chào', 'hello', 'hi', 'chào']):
                prompt = f"""Bạn là một trợ lý AI thân thiện. Hãy chào hỏi và giới thiệu về khả năng của bạn một cách tự nhiên bằng tiếng Việt.

Câu hỏi: {query}

Trả lời:"""
            elif any(word in query.lower() for word in ['cảm ơn', 'thank', 'thanks']):
                prompt = f"""Bạn là một trợ lý AI thân thiện. Hãy trả lời lời cảm ơn một cách lịch sự và thân thiện bằng tiếng Việt.

Câu hỏi: {query}

Trả lời:"""
            elif any(word in query.lower() for word in ['bạn là ai', 'bạn tên gì', 'giới thiệu']):
                prompt = f"""Bạn là trợ lý AI STEM thông minh. Hãy giới thiệu về bản thân và khả năng hỗ trợ trong lĩnh vực STEM một cách thân thiện bằng tiếng Việt.

Câu hỏi: {query}

Trả lời:"""
            elif any(word in query.lower() for word in ['hướng dẫn', 'cách sử dụng', 'help', 'giúp']):
                prompt = f"""Bạn là trợ lý AI hỗ trợ kỹ thuật. Hãy trả lời câu hỏi sau một cách chi tiết và hữu ích bằng tiếng Việt:

Câu hỏi: {query}

Trả lời:"""
            else:
                prompt = f"""Bạn là một trợ lý AI thông minh và thân thiện. Hãy trả lời câu hỏi sau một cách chi tiết, dễ hiểu và chính xác bằng tiếng Việt. Bạn có thể trả lời về bất kỳ chủ đề nào một cách hữu ích.

Câu hỏi: {query}

Trả lời:"""

            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = self._safe_generate_content(model, prompt)
            return response.text
            
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra khi xử lý câu hỏi: {str(e)}"
    
    def _fallback_to_gemini(self, query):
        """Fallback trực tiếp đến Gemini API"""
        return self._smart_fallback_to_gemini(query)
    
    def get_user_profile(self, user_id: str):
        """
        Lấy thông tin profile của user
        """
        return self.user_embedding_service.get_user_profile(user_id)
    
    def list_users_with_embeddings(self) -> List[str]:
        """
        Liệt kê tất cả users có embeddings
        """
        return self.user_embedding_service.list_all_users() 