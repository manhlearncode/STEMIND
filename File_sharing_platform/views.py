from unicodedata import category
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from .models import File, Category, Favorite, FileExtension
from django.conf import settings
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from django.http import HttpResponseRedirect
from Social_Platform.models import UserProfile, CustomUser
from Social_Platform.forms import UserProfileForm, CustomUserCreationForm
from Social_Platform.services.point_service import PointService
from django.utils import timezone
from datetime import timedelta
    

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
    top_users = CustomUser.objects.annotate(num_posts=Count('files')).order_by('-num_posts')[:10]
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

class RegisterForm(CustomUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'lastname', 'firstname', 'age', 'address', 'role', 'password1', 'password2']
    
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
        self.fields['lastname'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập họ của bạn'
        })
        self.fields['firstname'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tên của bạn'
        })
        self.fields['age'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập tuổi của bạn'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ công tác của bạn'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-control'
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
            messages.success(request, 'Tài khoản đã được tạo thành công!')
            
            # Kiểm tra xem user đã có đầy đủ thông tin cơ bản chưa
            if user.firstname and user.lastname and user.age and user.role:
                messages.success(request, 'Chào mừng bạn đến với STEMIND!')
                return redirect('home')
            else:
                messages.info(request, 'Vui lòng hoàn thiện thông tin cá nhân.')
                return redirect('basic_info')
    else:
        form = RegisterForm()
    context = {
        'form':form
    }
    return render(request, 'auth/register.html', context)

@login_required
def basic_info(request):
    """Trang điền thông tin cơ bản"""
    if request.method == 'POST':
        # Cập nhật thông tin cơ bản vào CustomUser
        user = request.user
        user.firstname = request.POST.get('firstname', '')
        user.lastname = request.POST.get('lastname', '')
        user.age = request.POST.get('age') or None
        user.address = request.POST.get('address', '')
        user.role = request.POST.get('role', '')
        user.save()
        
        messages.success(request, 'Thông tin cơ bản đã được cập nhật!')
        return redirect('complete_profile')
    
    # Hiển thị form với thông tin hiện tại
    context = {
        'user': request.user
    }
    return render(request, 'auth/basic_info.html', context)

@login_required
def complete_profile(request):
    """Trang điều thông tin sau đăng ký - chỉ cho bio và avatar"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
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
        top_users = CustomUser.objects.annotate(num_posts=Count('files', filter=Q(files__categories__in=child_cats))).order_by('-num_posts')[:10]
    else:
        # Nếu là category con, lấy files trực tiếp
        featured_files = File.objects.filter(file_status__in=[0, 1], categories=category).order_by('-file_downloads')[:3]
        recently_files = File.objects.filter(file_status__in=[0, 1], categories=category).order_by('-created_at')[:15]
        top_users = CustomUser.objects.annotate(num_posts=Count('files', filter=Q(files__categories=category))).order_by('-num_posts')[:10]
    
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
    
    # Handle points deduction for viewing files
    can_view = True
    point_message = None
    
    if request.user.is_authenticated:
        if file_obj.file_status == 1:  # For sale file - không trừ điểm khi view
            can_view = True
            # Không trừ điểm cho file for sale khi view
        else:  # Free file
            success, message = PointService.handle_view_free_file(request.user, file_obj.id)
            if not success:
                messages.error(request, f"Bạn cần ít nhất 1 điểm để xem tài liệu này. Hãy upload tài liệu để nhận điểm.")
                can_view = False
                return redirect('home')
            else:
                point_message = message
        
        if point_message:
            messages.info(request, point_message)
    
    # Lấy related files từ cùng categories
    related_files = File.objects.filter(file_status=1, categories__in=file_obj.categories.all()).exclude(id=file_obj.id).order_by('-file_downloads')[:5]
    top_users = CustomUser.objects.annotate(num_posts=Count('files', filter=Q(files__categories__in=file_obj.categories.all()))).order_by('-num_posts')[:5]
    
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
        'is_favorited': is_favorited,
        'can_view': can_view
    }
    return render(request, 'home/detail.html', context)

def download_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)
    
    # Handle points deduction for downloading files
    if request.user.is_authenticated:
        if file_obj.file_status == 1:  # For sale file - không trừ điểm khi download
            # Không trừ điểm cho file for sale khi download
            pass
        else:  # Free file
            success, message = PointService.handle_download_free_file(request.user, file_obj.id)
            if not success:
                messages.error(request, f"Bạn cần ít nhất 5 điểm để download tài liệu này. Hiện tại bạn có {PointService.get_user_points(request.user)} điểm.")
                return redirect('home')
            else:
                messages.info(request, message)
    
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
        form = FileUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.author = request.user
            
            # Kiểm tra quyền đăng tài liệu tính phí - tài khoản phải được tạo ít nhất 1 ngày
            if file_obj.file_status == 1:
                # Kiểm tra xem tài khoản đã được tạo ít nhất 1 ngày chưa
                one_day_ago = timezone.now() - timedelta(days=1)
                if request.user.date_joined > one_day_ago:
                    messages.error(request, 'Bạn cần có tài khoản ít nhất 1 ngày để đăng tài liệu có phí.')
                    context = {
                        'form': form,
                        'parent_categories': parent_categories,
                        'child_categories': child_categories
                    }
                    return render(request, 'home/upload.html', context)
            
            file_obj.save()
            form.save_m2m()  # <-- Thêm dòng này để lưu categories
            
            # Award points for file upload
            PointService.handle_file_upload(request.user, file_obj.id)
            
            messages.success(request, 'Tài liệu đã được tải lên thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Có lỗi xảy ra khi tải lên. Vui lòng kiểm tra lại thông tin.')
    else:
        form = FileUploadForm(user=request.user)
    
    # Kiểm tra quyền upload tài liệu có phí
    can_upload_paid = False
    if request.user.is_authenticated:
        one_day_ago = timezone.now() - timedelta(days=1)
        can_upload_paid = request.user.date_joined <= one_day_ago
    
    context = {
        'form': form,
        'parent_categories': parent_categories,
        'child_categories': child_categories,
        'can_upload_paid': can_upload_paid
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
    """Search files by title, description, category, author, or extension"""
    query = request.GET.get('q', '').strip()
    categories_filter = request.GET.getlist('categories')  # Lấy multiple categories
    status_filter = request.GET.get('status', '')
    extension_type_filter = request.GET.get('extension_type', '')  # Thêm extension type filter
    
    # Start with all files
    files = File.objects.filter(file_status__in=[0, 1])

    # Nếu có từ khóa, lọc thêm theo keyword
    if query:
        files = files.filter(
            Q(title__icontains=query) |
            Q(file_description__icontains=query) |
            Q(categories__name__icontains=query) |
            Q(author__username__icontains=query)
        )

    # Nếu có danh mục, lọc theo danh mục
    if categories_filter:
        files = files.filter(categories__name__in=categories_filter)

    # Nếu có trạng thái, lọc theo trạng thái
    if status_filter != '':
        try:
            files = files.filter(file_status=int(status_filter))
        except ValueError:
            pass  # hoặc xử lý nếu status không hợp lệ

    # Nếu có extension type, lọc theo extension type
    if extension_type_filter:
        files = files.filter(extension__extension_type=extension_type_filter)

    # Cuối cùng sắp xếp và loại bỏ duplicate
    files = files.distinct().order_by('-file_downloads', '-created_at')
    
    # Get categories for filter dropdown
    parent_categories = Category.objects.filter(parent__isnull=True)
    child_categories = Category.objects.filter(parent__isnull=False)
    
    # Get extension types for filter dropdown
    extension_types = FileExtension.EXTENSION_TYPES
    
    context = {
        'files': files,
        'parent_categories': parent_categories,
        'child_categories': child_categories,
        'extension_types': extension_types,
        'query': query,
        'selected_categories': categories_filter,  # Pass selected categories to template
        'selected_status': status_filter,
        'selected_extension_type': extension_type_filter,
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
    ).distinct().order_by('-file_downloads', '-created_at')[:10]
    
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
