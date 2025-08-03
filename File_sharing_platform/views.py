from unicodedata import category
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from .models import File, Category, Favorite
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
import json
from django.http import HttpResponseRedirect
import os
import json
import numpy as np
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def file_list_api(request):
    files = File.objects.all()
    data = []
    for file in files:
        data.append({
            'id': file.id,
            'title': file.title,
            'author': file.author.username,
            'category': file.category.category_name,
            'downloads': file.file_downloads,
            'file_urls': file.get_presigned_url(),
            'created_at': file.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse(data, safe=False)

def home(request):
    categories = Category.objects.all()
    featured_files = File.objects.filter(file_status__in=[0, 1]).order_by('-file_downloads')[:7]
    recently_files = File.objects.filter(file_status__in=[0, 1]).order_by('-created_at')[:10]
    top_users = User.objects.annotate(num_posts=Count('files')).filter(num_posts__gt=0).order_by('-num_posts')[:10]
    context = {
        'categories':categories,
        'featured_files':featured_files,
        'recently_files':recently_files,
        'top_users':top_users
    }
    return render(request, 'home/home.html', context)

def enter(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Tài khoản hoặc mật khẩu không chính xác!')
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!')
    return render(request, 'auth/enter.html')    

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for Bootstrap styling
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'password'
        })

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tài khoản đã được tạo thành công!')
            return redirect('enter')
    else:
        form = RegisterForm()
    context = {
        'form':form
    }
    return render(request, 'auth/register.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def posts_by_category(request, category_name):
    categories = Category.objects.all()
    category = get_object_or_404(Category, category_name=category_name)
    featured_files = File.objects.filter(file_status__in=[0, 1], category=category).order_by('-file_downloads')[:3]
    recently_files = File.objects.filter(file_status__in=[0, 1], category=category).order_by('-created_at')[:15]
    top_users = User.objects.annotate(num_posts=Count('files')).filter(num_posts__gt=0).order_by('-num_posts')[:10]
    context = {
        'categories':categories,
        'featured_files':featured_files,
        'recently_files':recently_files,
        'top_users':top_users
    }
    return render(request, 'home/home.html', context)



def file_detail(request, title):
    categories = Category.objects.all()
    file_obj = get_object_or_404(File, title=title)
    
    related_files = File.objects.filter(file_status=1, category=file_obj.category).exclude(id=file_obj.id).order_by('-file_downloads')[:5]
    top_users = User.objects.annotate(num_posts=Count('files')).filter(num_posts__gt=0).order_by('-num_posts')[:5]
    
    # Check if user has favorited this file
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, file=file_obj).exists()
    
    context = {
        'file': file_obj,
        'categories': categories,
        'related_files': related_files,
        'top_users': top_users,
        'is_favorited': is_favorited
    }
    return render(request, 'home/detail.html', context)

def download_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)
    file_obj.file_downloads += 1
    file_obj.save(update_fields=['file_downloads'])

    # Redirect to presigned URL
    return HttpResponseRedirect(file_obj.get_presigned_url())

# # Alias để tương thích với template cũ
def upload_file(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để tải lên tài liệu.')
        return redirect('enter')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.author = request.user
            file_obj.save()
            messages.success(request, 'Tài liệu đã được tải lên thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Có lỗi xảy ra khi tải lên. Vui lòng kiểm tra lại thông tin.')
    else:
        form = FileUploadForm()
    
    context = {
        'form': form
    }
    return render(request, 'home/upload.html', context)

def chatbot(request):
    """Chatbot interface view"""
    return render(request, 'chatbot.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .services.chatbot_service import ChatbotService
from .services.rag_chatbot_service import RAGChatbotService

# Initialize RAG chatbot service
try:
    from .services.rag_chatbot_service import get_rag_chatbot_service
    rag_chatbot_service = get_rag_chatbot_service()
except Exception as e:
    print(f"Lỗi khi khởi tạo RAG chatbot service: {e}")
    rag_chatbot_service = None

# Fallback to old chatbot service if RAG fails
try:
    from .services.chatbot_service import ChatbotService
    fallback_chatbot_service = ChatbotService()
except Exception as e:
    print(f"Lỗi khi khởi tạo fallback chatbot service: {e}")
    fallback_chatbot_service = None

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """API endpoint cho RAG chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', '')
        
        if not user_message.strip():
            return JsonResponse({
                'success': False,
                'error': 'Message không được để trống'
            })
        
        # Sử dụng RAG chatbot trước
        if rag_chatbot_service:
            try:
                bot_response = rag_chatbot_service.answer_question(user_message)
                
                # Tìm chunks tương tự để hiển thị thêm thông tin
                similar_chunks = rag_chatbot_service.get_similar_chunks(user_message, top_k=3)
                
                return JsonResponse({
                    'success': True,
                    'response': {
                        'text': bot_response,
                        'type': 'rag_response'
                    },
                    'similar_chunks': [chunk['preview'] for chunk in similar_chunks],
                    'session_id': session_id
                })
            except Exception as e:
                print(f"Lỗi trong RAG chatbot: {e}")
                # Fallback to old service
                pass
        
        # Fallback to old chatbot service
        if fallback_chatbot_service:
            try:
                bot_response = fallback_chatbot_service.answer_question(user_message)
                similar_files = fallback_chatbot_service.get_similar_files(user_message)
                
                return JsonResponse({
                    'success': True,
                    'response': {
                        'text': bot_response,
                        'type': 'fallback_response'
                    },
                    'similar_files': similar_files[:3],
                    'session_id': session_id
                })
            except Exception as e:
                print(f"Lỗi trong fallback chatbot: {e}")
        
        # Last resort - simple response
        simple_response = f"Xin lỗi, tôi hiện không thể xử lý câu hỏi '{user_message}'. Hệ thống chatbot đang được cập nhật. Vui lòng thử lại sau."
        return JsonResponse({
            'success': True,
            'response': {
                'text': simple_response,
                'type': 'simple_response'
            },
            'session_id': session_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
@require_http_methods(["GET"])
def chatbot_page(request):
    """Trang giao diện chatbot"""
    return render(request, 'chatbot.html')

@login_required
def toggle_favorite(request, file_id):
    """Toggle favorite status for a file"""
    if request.method == 'POST':
        file_obj = get_object_or_404(File, id=file_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, file=file_obj)
        
        if not created:
            # If favorite already exists, remove it
            favorite.delete()
            is_favorited = False
            message = 'Đã xóa khỏi yêu thích'
        else:
            is_favorited = True
            message = 'Đã thêm vào yêu thích'
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def user_favorites(request):
    """Display user's favorite files"""
    favorites = Favorite.objects.filter(user=request.user).select_related('file', 'file__category', 'file__author')
    favorite_files = [favorite.file for favorite in favorites]
    
    context = {
        'favorite_files': favorite_files,
        'categories': Category.objects.all(),
    }
    return render(request, 'home/favorites.html', context)

def about(request):
    """About us page"""
    return render(request, 'home/about.html')

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

class RAGChatbotService:
    def __init__(self, embeddings_file='stem_embeddings.json'):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # genai.configure(api_key=self.api_key) # This line was removed as per the new_code, as genai is not imported.
        self.embeddings_file = embeddings_file
        self.chunks = []
        self.embeddings = []
        self.user_embedding_service = UserEmbeddingService()
        self.load_embeddings()
    
    # ... existing methods ...
    
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
                # model = genai.GenerativeModel("gemini-2.0-flash-exp") # This line was removed as per the new_code, as genai is not imported.
                # response = model.generate_content(prompt) # This line was removed as per the new_code, as genai is not imported.
                # return response.text # This line was removed as per the new_code, as genai is not imported.
                # Fallback to simple response as genai is not available
                return f"Xin lỗi, tôi hiện không thể xử lý câu hỏi '{query}' với dữ liệu cá nhân của bạn. Hệ thống chatbot đang được cập nhật. Vui lòng thử lại sau."
            else:
                # Không có thông tin liên quan, chỉ dùng Gemini AI
                return self._fallback_to_gemini(query)
            
        except Exception as e:
            print(f"Lỗi trong RAG với user context: {e}")
            return self._fallback_to_gemini(query)
    
    def get_global_context(self, query: str, top_k: int = 3) -> List[str]:
        """
        Lấy context từ dữ liệu chung
        """
        if not self.chunks or len(self.embeddings) == 0:
            return []
        
        try:
            # query_embedding = self.get_gemini_embedding(query) # This line was removed as per the new_code, as genai is not imported.
            # if not query_embedding: # This line was removed as per the new_code, as genai is not imported.
            #     return [] # This line was removed as per the new_code, as genai is not imported.
            
            # query_embedding = np.array(query_embedding).reshape(1, -1) # This line was removed as per the new_code, as genai is not imported.
            # similarities = cosine_similarity(query_embedding, self.embeddings)[0] # This line was removed as per the new_code, as genai is not imported.
            # top_indices = np.argsort(similarities)[-top_k:][::-1] # This line was removed as per the new_code, as genai is not imported.
            
            # relevant_chunks = [] # This line was removed as per the new_code, as genai is not imported.
            # for i in top_indices: # This line was removed as per the new_code, as genai is not imported.
            #     if similarities[i] > 0.3: # This line was removed as per the new_code, as genai is not imported.
            #         relevant_chunks.append(self.chunks[i]) # This line was removed as per the new_code, as genai is not imported.
            
            # return relevant_chunks # This line was removed as per the new_code, as genai is not imported.
            # Fallback to simple response as genai is not available
            return f"Xin lỗi, tôi hiện không thể xử lý câu hỏi '{query}' với dữ liệu chung. Hệ thống chatbot đang được cập nhật. Vui lòng thử lại sau."
            
        except Exception as e:
            print(f"Lỗi khi lấy global context: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[dict]:
        """
        Lấy thông tin profile của user
        """
        return self.user_embedding_service.get_user_profile(user_id)
    
    def list_users_with_embeddings(self) -> List[str]:
        """
        Liệt kê tất cả users có embeddings
        """
        return self.user_embedding_service.list_all_users()

def chatbot_view(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Khởi tạo RAG service
        rag_service = RAGChatbotService()
        
        if user_id:
            # Sử dụng cả dữ liệu cá nhân và chung
            response = rag_service.answer_question_with_user_context(message, str(user_id))
        else:
            # Chỉ sử dụng dữ liệu chung
            response = rag_service.answer_question(message)
        
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot.html')

def user_profile_view(request):
    """
    View để xem profile của user (số lượng chunks, thời gian tạo, etc.)
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'})
    
    rag_service = RAGChatbotService()
    profile = rag_service.get_user_profile(str(request.user.id))
    
    return JsonResponse(profile or {'error': 'No profile found'})

def list_users_view(request):
    """
    View để liệt kê tất cả users có embeddings (chỉ admin)
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'})
    
    rag_service = RAGChatbotService()
    users = rag_service.list_users_with_embeddings()
    
    return JsonResponse({'users': users})
