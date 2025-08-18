import asyncio
import os
import json
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import openai
from .user_embedding_service import UserEmbeddingService

load_dotenv()

# Thiết lập tham số truy hồi mặc định từ .env
SIM_THRESHOLD = float(os.getenv("RAG_SIM_THRESHOLD", "0.5"))
DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "5"))

class UserEmbeddingService:
    def __init__(self):
        self._ensure_event_loop()
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

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
            relevant_chunks = [chunks[i] for i in top_indices if similarities[i] >= SIM_THRESHOLD]
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
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        openai.api_key = self.api_key
        # Runtime generation settings
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
        self.top_k = DEFAULT_TOP_K
        self.embeddings_file = embeddings_file
        self.chunks = []
        self.embeddings = []
        self.user_embedding_service = UserEmbeddingService()
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
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

    def get_openai_embedding(self, text):
        try:
            return self.embeddings_model.embed_query(text)
        except Exception as e:
            print(f"Lỗi khi tạo embedding OpenAI: {e}")
            return None

    def _generate_with_openai(self, prompt: str):
        """Sinh câu trả lời bằng OpenAI với system prompt chặt chẽ để giảm ảo giác"""
        try:
            response = openai.chat.completions.create(
                model=self.chat_model,  # hoặc model bạn có quyền dùng
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là trợ lý RAG tiếng Việt cho lĩnh vực STEM. \n"
                            "QUY ĐỊNH: \n"
                            "- ƯU TIÊN dùng đúng nội dung từ 'Ngữ liệu' được cung cấp (nếu có). \n"
                            "- Nếu ngữ liệu không đủ, nói rõ 'Chưa đủ ngữ liệu' và chỉ trả lời kiến thức nền ở mức tổng quát, tránh bịa đặt. \n"
                            "- Trình bày súc tích, có cấu trúc, dùng tiêu đề/ngắt đoạn, bullet khi phù hợp. \n"
                            "- Nêu rõ giả định (nếu có). \n"
                            "- Trả lời hoàn toàn bằng tiếng Việt."
                        ),
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
                # Nếu model không hỗ trợ temperature/max_tokens, thư viện sẽ xử lý ngoại lệ
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra khi xử lý: {str(e)}"

    def answer_question_with_user_context(self, query: str, user_id: str, top_k: int = None):
        if top_k is None:
            top_k = self.top_k
        try:
            user_chunks = self.user_embedding_service.get_user_context(user_id, query, top_k)
            global_chunks = self.get_global_context(query, top_k)
            all_chunks = user_chunks + global_chunks

            if not all_chunks:
                print("⚠️ Không có dữ liệu user hoặc global. Trả lời tổng quát kèm lưu ý thiếu ngữ liệu.")
                return self._generate_with_openai(self._build_prompt(query, []))

            prompt = self._build_prompt(query, all_chunks)
            answer = self._generate_with_openai(prompt)

            if not answer or len(answer.strip()) < 50:
                print("⚠️ Trả lời không hợp lệ. Sinh lại trả lời tổng quát.")
                return self._generate_with_openai(self._build_prompt(query, []))
            
            BAD_PHRASES = [
                "tôi không tìm thấy", 
                "không có thông tin",
                "không đủ dữ liệu", 
                "tài liệu không đề cập"
            ]
            if any(phrase in answer.lower() for phrase in BAD_PHRASES):
                print("⚠️ Trả lời không hợp lệ. Sinh lại trả lời tổng quát.")
                return self._generate_with_openai(self._build_prompt(query, []))
            
            return answer
        except Exception as e:
            print(f"Lỗi trong RAG với user context: {e}")
            return self._generate_with_openai(self._build_prompt(query, []))

    def answer_question(self, query, top_k: int = None):
        if top_k is None:
            top_k = self.top_k
        try:
            query_embedding = self.get_openai_embedding(query)
            if not query_embedding:
                return self._generate_with_openai(self._build_prompt(query, []))

            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            relevant_chunks = [self.chunks[i] for i in top_indices if similarities[i] >= SIM_THRESHOLD]

            if not relevant_chunks:
                print("⚠️ Không tìm được chunk phù hợp. Trả lời tổng quát.")
                return self._generate_with_openai(self._build_prompt(query, []))

            prompt = self._build_prompt(query, relevant_chunks)
            answer = self._generate_with_openai(prompt)

            if not answer or len(answer.strip()) < 50:
                print("⚠️ Trả lời không hợp lệ. Trả lời tổng quát.")
                return self._generate_with_openai(self._build_prompt(query, []))
            
            BAD_PHRASES = [
                "tôi không tìm thấy", 
                "không có thông tin",
                "không đủ dữ liệu", 
                "tài liệu không đề cập"
            ]
            if any(phrase in answer.lower() for phrase in BAD_PHRASES):
                return self._generate_with_openai(self._build_prompt(query, []))
            
            return answer
        except Exception as e:
            print(f"Lỗi trong RAG: {e}")
            return self._generate_with_openai(self._build_prompt(query, []))

    def get_global_context(self, query: str, top_k: int = None):
        if top_k is None:
            top_k = self.top_k
        if not self.chunks or len(self.embeddings) == 0:
            return []
        try:
            query_embedding = self.get_openai_embedding(query)
            if not query_embedding:
                return []
            query_embedding = np.array(query_embedding).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            return [self.chunks[i] for i in top_indices if similarities[i] >= SIM_THRESHOLD]
        except Exception as e:
            print(f"Lỗi khi lấy global context: {e}")
            return []

    def _build_prompt(self, query: str, context_chunks: List[str]) -> str:
        """Xây prompt rõ ràng, giảm ảo giác và tăng cấu trúc câu trả lời."""
        context_block = "\n".join([f"- {c}" for c in context_chunks]) if context_chunks else "(Không có ngữ liệu phù hợp)"
        guidance = (
            "YÊU CẦU TRẢ LỜI:\n"
            "1) Trả lời ngắn gọn, có cấu trúc (tiêu đề, mục, bullet khi cần).\n"
            "2) Dựa trên 'Ngữ liệu' nếu có. Nếu không đủ, nói rõ 'Chưa đủ ngữ liệu' và đưa gợi ý tổng quát, tránh bịa đặt.\n"
            "3) Nêu giả định (nếu có).\n"
            "4) Tiếng Việt, dễ hiểu cho giáo viên/học sinh."
        )
        prompt = (
            f"CÂU HỎI: {query}\n\n"
            f"NGỮ LIỆU:\n{context_block}\n\n"
            f"{guidance}\n\n"
            f"HÃY TRẢ LỜI:"
        )
        return prompt

    def get_user_profile(self, user_id: str):
        return self.user_embedding_service.get_user_profile(user_id)

    def list_users_with_embeddings(self) -> List[str]:
        return self.user_embedding_service.list_all_users()
