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

@csrf_exempt
def chatbot_api(request):
    """API endpoint for chatbot message processing"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            session_id = data.get('session_id', '')
            
            # Process the message and generate response
            response = process_chatbot_message(message)
            
            return JsonResponse({
                'success': True,
                'response': response,
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
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)

def process_chatbot_message(message):
    """Process chatbot message and generate appropriate response"""
    message_lower = message.lower()
    
    # STEM Education responses
    if any(word in message_lower for word in ['stem', 'giáo dục', 'education']):
        return {
            'text': 'STEM là viết tắt của Science (Khoa học), Technology (Công nghệ), Engineering (Kỹ thuật), và Mathematics (Toán học). Đây là phương pháp giáo dục tích hợp các lĩnh vực này để chuẩn bị cho học sinh thích ứng với thế giới công nghệ hiện đại.',
            'type': 'text'
        }
    
    # Programming/Coding responses
    elif any(word in message_lower for word in ['code', 'programming', 'lập trình', 'python', 'javascript']):
        return {
            'text': 'Lập trình là kỹ năng quan trọng trong thời đại số. Các ngôn ngữ phổ biến bao gồm Python, JavaScript, Java. Bạn muốn tìm hiểu về ngôn ngữ lập trình nào cụ thể không?',
            'type': 'text'
        }
    
    # Science responses
    elif any(word in message_lower for word in ['science', 'khoa học', 'physics', 'chemistry', 'biology']):
        return {
            'text': 'Khoa học là hệ thống kiến thức có tổ chức về vũ trụ, bao gồm vật lý, hóa học, sinh học và nhiều lĩnh vực khác. Bạn quan tâm đến lĩnh vực khoa học nào?',
            'type': 'text'
        }
    
    # Math responses
    elif any(word in message_lower for word in ['math', 'toán', 'toán học', 'calculation']):
        return {
            'text': 'Toán học là nền tảng của tất cả các ngành khoa học. Nó bao gồm đại số, hình học, giải tích và nhiều lĩnh vực khác. Bạn cần hỗ trợ về chủ đề toán học nào?',
            'type': 'text'
        }
    
    # Technology responses
    elif any(word in message_lower for word in ['technology', 'công nghệ', 'ai', 'artificial intelligence', 'machine learning']):
        return {
            'text': 'Công nghệ đang phát triển nhanh chóng, đặc biệt là AI và Machine Learning. Những công nghệ này đang thay đổi cách chúng ta học tập và làm việc.',
            'type': 'text'
        }
    
    # Greeting responses
    elif any(word in message_lower for word in ['hello', 'hi', 'xin chào', 'chào']):
        return {
            'text': 'Xin chào! Tôi là trợ lý AI của STEMind. Tôi có thể giúp bạn tìm hiểu về STEM, lập trình, khoa học và nhiều chủ đề khác. Bạn muốn tìm hiểu về điều gì?',
            'type': 'text'
        }
    
    # Help responses
    elif any(word in message_lower for word in ['help', 'giúp', 'hỗ trợ', 'support']):
        return {
            'text': 'Tôi có thể giúp bạn với:\n• Thông tin về giáo dục STEM\n• Hướng dẫn lập trình\n• Giải thích các khái niệm khoa học\n• Hỗ trợ toán học\n• Tìm kiếm tài liệu học tập\nBạn cần hỗ trợ gì cụ thể?',
            'type': 'text'
        }
    
    # Default response
    else:
        return {
            'text': 'Cảm ơn bạn đã hỏi! Tôi là trợ lý AI được thiết kế để hỗ trợ giáo dục STEM. Bạn có thể hỏi tôi về khoa học, công nghệ, kỹ thuật, toán học hoặc bất kỳ chủ đề nào khác. Tôi sẽ cố gắng hết sức để giúp bạn!',
            'type': 'text'
        }

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
