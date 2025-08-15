import os
import json
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class UserEmbeddingService:
    def __init__(self):
        # Sử dụng OpenAI embeddings
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")  
        # Hoặc "text-embedding-3-large" nếu cần độ chính xác cao hơn
    
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
            
            # Lấy các chunk có similarity > 0.3
            relevant_chunks = []
            for i in top_indices:
                if similarities[i] > 0.3:
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
