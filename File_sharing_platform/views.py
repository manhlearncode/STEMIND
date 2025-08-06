from unicodedata import category
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from .models import File, Category, Favorite
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from django.http import HttpResponseRedirect
from Social_Platform.models import UserProfile
from Social_Platform.forms import UserProfileForm
    

def file_list_api(request):
    files = File.objects.all()
    data = []
    for file in files:
        categories_str = ", ".join([cat.name for cat in file.categories.all()])
        data.append({
            'id': file.id,
            'title': file.title,
            'author': file.author.username,
            'categories': categories_str,
            'downloads': file.file_downloads,
            'file_urls': file.get_presigned_url(),
            'created_at': file.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse(data, safe=False)

def home(request):
    # Lấy categories cha và con
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    
    featured_files = File.objects.filter(file_status__in=[0, 1]).order_by('-file_downloads')[:7]
    recently_files = File.objects.filter(file_status__in=[0, 1]).order_by('-created_at')[:10]
    top_users = User.objects.annotate(num_posts=Count('files')).order_by('-num_posts')[:10]
    context = {
        'parent_categories': parent_categories,
        'child_categories': child_categories,
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
            user = form.save()
            # Tự động đăng nhập sau khi đăng ký
            login(request, user)
            messages.success(request, 'Tài khoản đã được tạo thành công! Vui lòng hoàn thiện thông tin cá nhân.')
            return redirect('complete_profile')
    else:
        form = RegisterForm()
    context = {
        'form':form
    }
    return render(request, 'auth/register.html', context)

@login_required
def complete_profile(request):
    """Trang điều thông tin sau đăng ký"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đăng ký hoàn tất! Chào mừng bạn đến với STEMIND!')
            return redirect('home')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'auth/complete_profile.html', context)

def user_logout(request):
    logout(request)
    return redirect('home')

def posts_by_category(request, category_name):
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    category = get_object_or_404(Category, name=category_name)
    
    # Nếu là category cha, lấy tất cả files của các category con
    if category.is_parent:
        child_cats = category.get_all_children()
        featured_files = File.objects.filter(file_status__in=[0, 1], categories__in=child_cats).order_by('-file_downloads')[:3]
        recently_files = File.objects.filter(file_status__in=[0, 1], categories__in=child_cats).order_by('-created_at')[:15]
        top_users = User.objects.annotate(num_posts=Count('files', filter=Q(files__categories__in=child_cats))).order_by('-num_posts')[:10]
    else:
        # Nếu là category con, lấy files trực tiếp
        featured_files = File.objects.filter(file_status__in=[0, 1], categories=category).order_by('-file_downloads')[:3]
        recently_files = File.objects.filter(file_status__in=[0, 1], categories=category).order_by('-created_at')[:15]
        top_users = User.objects.annotate(num_posts=Count('files', filter=Q(files__categories=category))).order_by('-num_posts')[:10]
    
    context = {
        'parent_categories': parent_categories,
        'child_categories': child_categories,
        'featured_files':featured_files,
        'recently_files':recently_files,
        'top_users':top_users
    }
    return render(request, 'home/home.html', context)

def get_presigned_url(self):
    import boto3
    from django.conf import settings

    s3 = boto3.client('s3')
    return s3.generate_presigned_url('get_object', Params={
        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
        'Key': self.file_urls.name
    }, ExpiresIn=3600)
    return url

def file_detail(request, title):
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    file_obj = get_object_or_404(File, title=title)
    
    # Lấy related files từ cùng categories
    related_files = File.objects.filter(file_status=1, categories__in=file_obj.categories.all()).exclude(id=file_obj.id).order_by('-file_downloads')[:5]
    top_users = User.objects.annotate(num_posts=Count('files', filter=Q(files__categories__in=file_obj.categories.all()))).order_by('-num_posts')[:5]
    
    # Check if user has favorited this file
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, file=file_obj).exists()
    
    context = {
        'file': file_obj,
        'parent_categories': parent_categories,
        'child_categories': child_categories,
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
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để tải lên tài liệu.')
        return redirect('enter')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.author = request.user
            file_obj.save()
            form.save_m2m()  # <-- Thêm dòng này để lưu categories
            messages.success(request, 'Tài liệu đã được tải lên thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Có lỗi xảy ra khi tải lên. Vui lòng kiểm tra lại thông tin.')
    else:
        form = FileUploadForm()
    
    context = {
        'form': form,
        'parent_categories': parent_categories,
        'child_categories': child_categories
    }
    return render(request, 'home/upload.html', context)

def chatbot(request):
    """Chatbot interface view"""
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
    favorites = Favorite.objects.filter(user=request.user).select_related('file', 'file__author')
    favorite_files = [favorite.file for favorite in favorites]
    
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    
    context = {
        'favorite_files': favorite_files,
        'parent_categories': parent_categories,
        'child_categories': child_categories,
    }
    return render(request, 'home/favorites.html', context)

def about(request):
    """About us page"""
    return render(request, 'home/about.html')

def search_files(request):
    """Search files by title, description, category, or author"""
    query = request.GET.get('q', '').strip()
    categories_filter = request.GET.getlist('categories')  # Lấy multiple categories
    status_filter = request.GET.get('status', '')
    
    # Start with all files
    files = File.objects.filter(file_status__in=[0, 1])
    
    if query:
        # Search in title, description, category name, and author username
        files = files.filter(
            Q(title__icontains=query) |
            Q(file_description__icontains=query) |
            Q(categories__name__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    if categories_filter:
        # Filter by multiple categories (OR logic)
        category_q = Q()
        for category_name in categories_filter:
            category_q |= Q(categories__name=category_name)
        files = files.filter(category_q)
    
    if status_filter:
        files = files.filter(file_status=int(status_filter))
    
    # Order by downloads and creation date
    files = files.order_by('-file_downloads', '-created_at')
    
    # Get categories for filter dropdown
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    
    context = {
        'files': files,
        'parent_categories': parent_categories,
        'child_categories': child_categories,
        'query': query,
        'selected_categories': categories_filter,  # Pass selected categories to template
        'selected_status': status_filter,
        'total_results': files.count()
    }
    
    return render(request, 'home/search.html', context)

def search_api(request):
    """API endpoint for real-time search"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'files': [], 'total': 0})
    
    files = File.objects.filter(
        file_status__in=[0, 1]
    ).filter(
        Q(title__icontains=query) |
        Q(file_description__icontains=query) |
        Q(categories__name__icontains=query) |
        Q(author__username__icontains=query)
    ).order_by('-file_downloads', '-created_at')[:10]
    
    data = []
    for file in files:
        categories_str = ", ".join([cat.name for cat in file.categories.all()])
        data.append({
            'id': file.id,
            'title': file.title,
            'description': file.file_description[:100] + '...' if file.file_description and len(file.file_description) > 100 else file.file_description,
            'categories': categories_str,
            'author': file.author.username,
            'downloads': file.file_downloads,
            'created_at': file.created_at.strftime('%Y-%m-%d'),
            'status': 'Free' if file.file_status == 0 else 'For sale',
            'url': f'/file/{file.title}/'
        })
    
    return JsonResponse({'files': data, 'total': files.count()})
