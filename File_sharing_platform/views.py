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

def toggle_favorite(request, file_id):
    file = get_object_or_404(File, id=file_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, file=file)
    if not created:
        favorite.delete()
    return JsonResponse({'success': True})

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
