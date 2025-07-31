import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self, embeddings_file='embeddings.json'):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.embeddings_file = embeddings_file
        self.chunks = []
        self.embeddings = []
        self.load_embeddings()
    
    def load_embeddings(self):
        """Load embeddings từ file JSON"""
        if os.path.exists(self.embeddings_file):
            with open(self.embeddings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = data.get('chunks', [])
                self.embeddings = np.array(data.get('embeddings', []))
        else:
            print(f"File embeddings không tồn tại: {self.embeddings_file}")
    
    def create_embedding(self, text):
        """Tạo embedding cho text"""
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        return embeddings.embed_query(text)
    
    def answer_question(self, query, top_k=3):
        """Trả lời câu hỏi dựa trên embeddings"""
        if not self.chunks or len(self.embeddings) == 0:
            return "Xin lỗi, chatbot chưa được train. Vui lòng chạy lệnh train trước."
        
        try:
            # Tạo embedding cho câu hỏi
            query_embedding = np.array(self.create_embedding(query)).reshape(1, -1)
            
            # Tính similarity
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Lấy top_k chunks giống nhất
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            top_chunks = [self.chunks[i] for i in top_indices]
            top_scores = [similarities[i] for i in top_indices]
            
            # Tạo context từ top chunks
            context = "\n".join(top_chunks)
            
            # Generate response với Gemini
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            prompt = f"""
            Context (dữ liệu từ hệ thống):
            {context}
            
            Câu hỏi của người dùng: {query}
            
            Hãy trả lời câu hỏi dựa trên context trên. Nếu không có thông tin liên quan trong context, hãy nói rằng bạn không có thông tin về vấn đề này.
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Xin lỗi, có lỗi xảy ra: {str(e)}"
    
    def get_similar_files(self, query, limit=5):
        """Tìm files tương tự dựa trên câu hỏi"""
        if not self.chunks or len(self.embeddings) == 0:
            return []
        
        try:
            query_embedding = np.array(self.create_embedding(query)).reshape(1, -1)
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Lấy top chunks liên quan đến files
            file_related_indices = []
            for i, chunk in enumerate(self.chunks):
                if chunk.startswith("File:"):
                    file_related_indices.append(i)
            
            if not file_related_indices:
                return []
            
            # Tính similarity chỉ với file-related chunks
            file_similarities = [similarities[i] for i in file_related_indices]
            top_file_indices = np.argsort(file_similarities)[-limit:][::-1]
            
            return [self.chunks[file_related_indices[i]] for i in top_file_indices]
            
        except Exception as e:
            print(f"Lỗi khi tìm files tương tự: {e}")
            return [] 