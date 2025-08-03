import os
import json
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import django
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Chalk.settings')
django.setup()

from File_sharing_platform.models import File, Category
from Social_Platform.models import Post, Comment
from typing import List
import PyPDF2
import docx
import requests
import tempfile
import re
from collections import Counter
from typing import List


def lay_url_tai_lieu_cua_nguoi_dung(user_id: str) -> list:
    """
    Truy vấn cơ sở dữ liệu để lấy danh sách URL tài liệu mà người dùng đã upload.
    Trả về danh sách các URL.
    """
    from File_sharing_platform.models import File

    files = File.objects.filter(author__id=user_id)
    url_list = []
    for file in files:
        # Giả sử trường url là file.url
        if hasattr(file, 'url'):
            url_list.append(file.url)
        # Nếu trường url có tên khác, ví dụ file.file_url:
        # if hasattr(file, 'file_url'):
        #     url_list.append(file.file_url)
    return url_list

def tai_va_doc_file_tu_url(url: str) -> str:
    """
    Tải file từ URL về máy tạm thời, sau đó trích xuất nội dung văn bản (PDF, DOCX, TXT).
    Trả về chuỗi văn bản.
    """
    import PyPDF2
    import docx

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Không thể tải file từ URL: {url}")

    # Lưu file tạm thời
    suffix = url.split('.')[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + suffix) as tmp_file:
        tmp_file.write(response.content)
        tmp_path = tmp_file.name

    text = ""
    try:
        if suffix == "pdf":
            with open(tmp_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        elif suffix == "docx":
            doc = docx.Document(tmp_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif suffix == "txt":
            with open(tmp_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise Exception("Định dạng file không hỗ trợ: " + suffix)
    finally:
        os.remove(tmp_path)
    return text


def phan_tich_phong_cach_viet(texts: List[str], user_id: str):
    """
    Phân tích các đoạn văn bản để xác định phong cách viết:
    - Độ dài câu trung bình
    - Xu hướng cảm xúc (rất đơn giản: đếm số từ tích cực/tiêu cực)
    - Các cụm từ/cấu trúc thường lặp lại
    Lưu kết quả vào writing_profile_<user_id>.json
    """
    # Danh sách từ cảm xúc đơn giản (có thể mở rộng)
    positive_words = {"tốt", "hay", "đẹp", "tuyệt", "vui", "hài lòng", "thành công"}
    negative_words = {"xấu", "tệ", "buồn", "thất bại", "khó", "không hài lòng"}

    all_sentences = []
    all_words = []
    positive_count = 0
    negative_count = 0
    phrase_counter = Counter()

    for text in texts:
        # Tách câu
        sentences = re.split(r'[.!?\\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        all_sentences.extend(sentences)
        # Tách từ
        words = re.findall(r'\\w+', text.lower())
        all_words.extend(words)
        # Đếm cảm xúc
        positive_count += sum(1 for w in words if w in positive_words)
        negative_count += sum(1 for w in words if w in negative_words)
        # Đếm cụm từ 2-3 từ lặp lại
        for n in [2, 3]:
            ngrams = zip(*[words[i:] for i in range(n)])
            for ng in ngrams:
                phrase_counter[' '.join(ng)] += 1

    avg_sentence_length = sum(len(s.split()) for s in all_sentences) / len(all_sentences) if all_sentences else 0
    most_common_phrases = phrase_counter.most_common(10)
    sentiment = "tích cực" if positive_count > negative_count else "tiêu cực" if negative_count > positive_count else "trung tính"

    profile = {
        "avg_sentence_length": avg_sentence_length,
        "sentiment": sentiment,
        "positive_word_count": positive_count,
        "negative_word_count": negative_count,
        "most_common_phrases": most_common_phrases
    }

    out_path = f"writing_profile_{user_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu profile phân tích phong cách viết vào {out_path}")

def ket_hop_du_lieu_embedding(user_id: str):
    """
    Tải embedding từ file "global_data.json" (dữ liệu chung) và "user_<user_id>_data.json" (dữ liệu cá nhân),
    sau đó kết hợp thành một danh sách dùng cho truy xuất văn bản (RAG).
    Trả về tuple (all_chunks, all_embeddings)
    """
    import os

    global_file = "global_data.json"
    user_file = f"user_{user_id}_data.json"

    all_chunks = []
    all_embeddings = []

    # Load global data
    if os.path.exists(global_file):
        with open(global_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_chunks.extend(data.get("chunks", []))
            all_embeddings.extend(data.get("embeddings", []))

    # Load user data
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_chunks.extend(data.get("chunks", []))
            all_embeddings.extend(data.get("embeddings", []))

    return all_chunks, np.array(all_embeddings)

def tao_prompt_ca_nhan_hoa(truy_van: str, context_chunks: List[str], profile_viet: dict):
    """
    Xây dựng prompt đầu vào cho mô hình ngôn ngữ, kết hợp:
    - Các đoạn văn bản liên quan đến truy vấn người dùng (context_chunks)
    - Thông tin về phong cách viết của người dùng (profile_viet)
    """
    context = "\n".join(context_chunks)
    phong_cach = []
    if profile_viet:
        if profile_viet.get("sentiment"):
            phong_cach.append(f"Xu hướng cảm xúc: {profile_viet['sentiment']}")
        if profile_viet.get("avg_sentence_length"):
            phong_cach.append(f"Độ dài câu trung bình: {profile_viet['avg_sentence_length']:.1f} từ")
        if profile_viet.get("most_common_phrases"):
            phrases = [f'"{p[0]}" ({p[1]} lần)' for p in profile_viet["most_common_phrases"]]
            phong_cach.append(f"Cụm từ/cấu trúc thường dùng: {', '.join(phrases)}")
    phong_cach_str = "\n".join(phong_cach)

    prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Hãy trả lời truy vấn của người dùng dựa trên các đoạn tài liệu liên quan và mô phỏng phong cách viết của người dùng như sau:

Thông tin về phong cách viết của người dùng:
{phong_cach_str}

Các đoạn tài liệu liên quan:
{context}

Truy vấn: {truy_van}

Yêu cầu: Trả lời đúng nội dung, sử dụng văn phong, cấu trúc câu và cảm xúc giống người dùng nhất có thể. Trả lời bằng tiếng Việt.

Trả lời:"""
    return prompt

def tra_loi_ca_nhan_hoa(truy_van: str, user_id: str):
    """
    Hàm tổng điều phối:
    - Lấy danh sách file tài liệu người dùng từ CSDL
    - Tạo embedding và phân tích phong cách viết nếu chưa có
    - Kết hợp dữ liệu embedding cá nhân + chung
    - Sinh câu trả lời dựa trên phong cách người dùng nếu có
    """
    import os

    # 1. Lấy danh sách URL file tài liệu người dùng
    url_list = lay_url_tai_lieu_cua_nguoi_dung(user_id)
    user_data_file = f"user_{user_id}_data.json"
    writing_profile_file = f"writing_profile_{user_id}.json"

    # 2. Nếu chưa có embedding cá nhân, tạo embedding từ tài liệu người dùng
    if not os.path.exists(user_data_file):
        van_ban_list = []
        for url in url_list:
            try:
                text = tai_va_doc_file_tu_url(url)
                if text.strip():
                    van_ban_list.append(text)
            except Exception as e:
                print(f"Lỗi xử lý file {url}: {e}")
        if van_ban_list:
            tao_embedding_va_luu_json(van_ban_list, user_id)
            phan_tich_phong_cach_viet(van_ban_list, user_id)

    # 3. Kết hợp embedding cá nhân + chung
    all_chunks, all_embeddings = ket_hop_du_lieu_embedding(user_id)

    # 4. Tải profile phong cách viết nếu có
    profile_viet = None
    if os.path.exists(writing_profile_file):
        with open(writing_profile_file, "r", encoding="utf-8") as f:
            profile_viet = json.load(f)

    # 5. Tạo embedding cho truy vấn và tìm các chunk liên quan
    from sklearn.metrics.pairwise import cosine_similarity
    chatbot = get_rag_chatbot_service()
    if chatbot is None:
        return "Không thể khởi tạo dịch vụ chatbot."

    query_embedding = chatbot.get_gemini_embedding(truy_van)
    if not query_embedding:
        return chatbot._fallback_to_gemini(truy_van)
    query_embedding = np.array(query_embedding).reshape(1, -1)
    similarities = cosine_similarity(query_embedding, all_embeddings)[0]
    top_k = 3
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    top_chunks = [all_chunks[i] for i in top_indices if similarities[i] > 0.3]

    # 6. Sinh prompt cá nhân hóa nếu có phong cách viết
    if top_chunks:
        prompt = tao_prompt_ca_nhan_hoa(truy_van, top_chunks, profile_viet)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text
    else:
        # Nếu không có chunk liên quan, chỉ dùng Gemini AI
        return chatbot._fallback_to_gemini(truy_van)

def tao_embedding_ca_nhan_nguoi_dung(user_id: str):
    """
    Truy vấn các URL tài liệu của user, tải về, trích xuất nội dung, chunk, tạo embedding,
    và lưu vào file user_<user_id>_data.json.
    """
    url_list = lay_url_tai_lieu_cua_nguoi_dung(user_id)
    van_ban_list = []
    for url in url_list:
        try:
            text = tai_va_doc_file_tu_url(url)
            if text.strip():
                van_ban_list.append(text)
        except Exception as e:
            print(f"Lỗi xử lý file {url}: {e}")

    if van_ban_list:
        tao_embedding_va_luu_json(van_ban_list, user_id)
        phan_tich_phong_cach_viet(van_ban_list, user_id)
    else:
        print(f"Không có dữ liệu hợp lệ cho user {user_id}")

def tao_embedding_va_luu_json(van_ban_list: List[str], user_id: str):
    """
    Nhận vào danh sách văn bản từ nhiều file của người dùng,
    chia nhỏ từng văn bản thành các đoạn (chunk), tạo embedding bằng Gemini,
    và lưu embedding vào file "user_<user_id>_data.json".
    """
    all_chunks = []
    all_embeddings = []
    chunk_size = 500
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    for van_ban in van_ban_list:
        # Chia nhỏ văn bản thành các chunk
        words = van_ban.split()
        chunks = []
        current_chunk = []
        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        # Tạo embedding cho từng chunk
        for chunk in chunks:
            embedding = embeddings_model.embed_query(chunk)
            all_chunks.append(chunk)
            all_embeddings.append(embedding)

    data = {
        'chunks': all_chunks,
        'embeddings': all_embeddings
    }
    file_name = f"user_{user_id}_data.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu {len(all_chunks)} chunks và embeddings vào {file_name}")

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
                # Có thông tin liên quan, sử dụng RAG + Gemini
                context = "\n".join(relevant_chunks)
                prompt = f"""Bạn là trợ lý AI lĩnh vực STEM. Dựa trên các đoạn tài liệu sau, hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và chính xác.

    Tài liệu liên quan:
    {context}

    Câu hỏi: {query}

    Hãy trả lời bằng tiếng Việt, sử dụng thông tin từ tài liệu trên. Nếu cần, bạn có thể bổ sung kiến thức tổng quát của mình để giải thích rõ hơn.

    Trả lời:"""
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                response = model.generate_content(prompt)
                return response.text
            else:
                # Không có thông tin liên quan, chỉ dùng Gemini AI
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

def load_user_embeddings(user_id):
    """Load embeddings của user cụ thể"""
    filename = f"user_{user_id}_embeddings.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['chunks'], np.array(data['embeddings'])
    return [], np.array([])

class Command(BaseCommand):
    help = 'Train RAG chatbot by creating embeddings from database data'
    
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
        
        if all_users:
            # Tạo embeddings cho tất cả users
            self.stdout.write("Tạo embeddings cho tất cả users...")
            self.create_embeddings_for_all_users(chunk_size)
        elif user_id:
            # Tạo embeddings cá nhân cho user cụ thể
            self.stdout.write(f"Tạo embeddings cá nhân cho user {user_id}...")
            self.create_user_embeddings(user_id, chunk_size)
            self.stdout.write(
                self.style.SUCCESS(f'Đã tạo embeddings cá nhân cho user {user_id}')
            )
        else:
            # Tạo embeddings chung từ database
            self.stdout.write("Tạo embeddings chung từ database...")
            rag_service = RAGChatbotService(embeddings_file)
            rag_service.create_embeddings_from_database()
            self.stdout.write(
                self.style.SUCCESS(f'Đã tạo embeddings và lưu vào {embeddings_file}')
            )
    
    def create_embeddings_for_all_users(self, chunk_size):
        """Tạo embeddings cho tất cả users"""
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
        """Tạo embeddings riêng cho một user"""
        all_chunks = []
        all_embeddings = []
        
        try:
            # Lấy dữ liệu từ File sharing platform của user
            files = File.objects.filter(author__id=user_id)
            for file in files:
                text = f"File: {file.title}\n"
                if file.file_description:
                    text += f"Mô tả: {file.file_description}\n"
                text += f"Danh mục: {file.category.category_name}\n"
                text += f"Tác giả: {file.author.username}\n"
                
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Lấy dữ liệu từ Social platform của user
            posts = Post.objects.filter(author__id=user_id)
            for post in posts:
                text = f"Post từ {post.author.username}: {post.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Lấy comments của user
            comments = Comment.objects.filter(user__id=user_id)
            for comment in comments:
                text = f"Comment từ {comment.user.username}: {comment.content}\n"
                chunks = self.chunk_text(text, chunk_size)
                for chunk in chunks:
                    embedding = self.get_gemini_embedding(chunk)
                    if embedding:
                        all_chunks.append(chunk)
                        all_embeddings.append(embedding)
            
            # Lưu vào file JSON riêng cho user
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
        """Tạo embedding cho text sử dụng Gemini"""
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            return embeddings.embed_query(text)
        except Exception as e:
            self.stdout.write(f"Lỗi khi tạo embedding: {e}")
            return None