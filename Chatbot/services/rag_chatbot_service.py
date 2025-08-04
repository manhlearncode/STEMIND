import asyncio
import concurrent.futures
import os
import json
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import google.generativeai as genai
from .user_embedding_service import UserEmbeddingService

load_dotenv()

class UserEmbeddingService:
    def __init__(self):
        self._ensure_event_loop()
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    def _ensure_event_loop(self):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

    def load_user_embeddings(self, user_id: str) -> Tuple[List[str], np.ndarray]:
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
        self._ensure_event_loop()
        chunks, embeddings = self.load_user_embeddings(user_id)
        if len(chunks) == 0 or len(embeddings) == 0:
            return []
        try:
            query_embedding = self.embeddings_model.embed_query(query)
            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            relevant_chunks = [chunks[i] for i in top_indices if similarities[i] > 0.3]
            return relevant_chunks
        except Exception as e:
            print(f"Lỗi khi tìm context cho user {user_id}: {e}")
            return []

    def get_user_profile(self, user_id: str) -> Optional[dict]:
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
        users = []
        for filename in os.listdir('.'):
            if filename.startswith('user_') and filename.endswith('_embeddings.json'):
                user_id = filename.replace('user_', '').replace('_embeddings.json', '')
                users.append(user_id)
        return users


class RAGChatbotService:
    def __init__(self, embeddings_file='stem_embeddings.json'):
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
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            print(f"Lỗi khi tạo embedding: {e}")
            return None

    def answer_question_with_user_context(self, query: str, user_id: str, top_k: int = 3):
        try:
            user_chunks = self.user_embedding_service.get_user_context(user_id, query, top_k)
            global_chunks = self.get_global_context(query, top_k)
            all_chunks = user_chunks + global_chunks
            if all_chunks:
                context = "\n".join(all_chunks)
                prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Dựa trên các đoạn tài liệu sau (bao gồm cả dữ liệu cá nhân và dữ liệu chung), hãy trả lời câu hỏi: {query}\n\nTài liệu:\n{context}\n\nTrả lời:"""
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(prompt)
                return response.text
            else:
                return self._fallback_to_gemini(query)
        except Exception as e:
            print(f"Lỗi trong RAG với user context: {e}")
            return self._fallback_to_gemini(query)

    def answer_question(self, query, top_k=3):
        try:
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return self._fallback_to_gemini(query)

            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            relevant_chunks = [self.chunks[i] for i in top_indices if similarities[i] > 0.3]

            if relevant_chunks:
                context = "\n".join(relevant_chunks)
                prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Dựa trên tài liệu sau, hãy trả lời câu hỏi: {query}\n\nTài liệu:\n{context}\n\nTrả lời:"""
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(prompt)
                return response.text
            else:
                return self._fallback_to_gemini(query)
        except Exception as e:
            print(f"Lỗi trong RAG: {e}")
            return self._fallback_to_gemini(query)

    def get_global_context(self, query: str, top_k: int = 3):
        if not self.chunks or len(self.embeddings) == 0:
            return []
        try:
            query_embedding = self.get_gemini_embedding(query)
            if not query_embedding:
                return []
            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            return [self.chunks[i] for i in top_indices if similarities[i] > 0.3]
        except Exception as e:
            print(f"Lỗi khi lấy global context: {e}")
            return []

    def _fallback_to_gemini(self, query):
        try:
            prompt = f"""Bạn là một trợ lý AI thông minh. Hãy trả lời câu hỏi sau: {query}\n\nTrả lời:"""
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra khi xử lý: {str(e)}"

    def get_user_profile(self, user_id: str):
        return self.user_embedding_service.get_user_profile(user_id)

    def list_users_with_embeddings(self) -> List[str]:
        return self.user_embedding_service.list_all_users()
