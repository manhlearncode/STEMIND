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

def get_presigned_url(self):
    import boto3
    from django.conf import settings

    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    key = self.file_urls.name  # đường dẫn trong bucket

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600
    )
    return url

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
