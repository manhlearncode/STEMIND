from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Like, Comment, UserProfile
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User

# Create your views here.

@login_required
def feed(request):
    # Get all posts for now (simplified version)
    posts = Post.objects.all().select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')
    
    # Thêm presigned URLs cho posts
    for post in posts:
        post.image_url = post.get_image_presigned_url() if post.image else None
        if hasattr(post.author, 'userprofile'):
            post.author.userprofile.avatar_url = post.author.userprofile.get_avatar_presigned_url() if post.author.userprofile.avatar else None
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('social:feed')
    else:
        form = PostForm()
    
    context = {
        'posts': posts,
        'form': form,
    }
    return render(request, 'social/feed.html', context)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.like_count()
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'content': comment.content,
                'user': comment.user.username,
                'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p')
            })
    
    return JsonResponse({'success': False})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    liked_posts = Post.objects.filter(likes__user=user).order_by('-created_at')
    
    # Thêm presigned URLs cho posts
    for post in posts:
        post.image_url = post.get_image_presigned_url() if post.image else None
    
    for post in liked_posts:
        post.image_url = post.get_image_presigned_url() if post.image else None
        if hasattr(post.author, 'userprofile'):
            post.author.userprofile.avatar_url = post.author.userprofile.get_avatar_presigned_url() if post.author.userprofile.avatar else None
    
    # Check if current user is following this profile
    is_following = False
    profile = None
    try:
        profile = user.userprofile
        if request.user != user:
            is_following = profile.followers.filter(id=request.user.id).exists()
        # Thêm avatar URL cho profile
        profile.avatar_url = profile.get_avatar_presigned_url() if profile.avatar else None
    except UserProfile.DoesNotExist:
        is_following = False
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'liked_posts': liked_posts,
        'is_following': is_following,
    }
    return render(request, 'social/profile.html', context)

@login_required
def liked_posts(request):
    """Display user's liked posts"""
    liked_posts = Post.objects.filter(likes__user=request.user).select_related('author').order_by('-created_at')
    
    # Thêm presigned URLs cho posts
    for post in liked_posts:
        post.image_url = post.get_image_presigned_url() if post.image else None
        if hasattr(post.author, 'userprofile'):
            post.author.userprofile.avatar_url = post.author.userprofile.get_avatar_presigned_url() if post.author.userprofile.avatar else None
    
    context = {
        'posts': liked_posts,
        'title': 'Liked Posts'
    }
    return render(request, 'social/liked_posts.html', context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user != user_to_follow:
        profile, created = UserProfile.objects.get_or_create(user=user_to_follow)
        
        if request.user in profile.followers.all():
            profile.followers.remove(request.user)
            is_following = False
        else:
            profile.followers.add(request.user)
            is_following = True
        
        return JsonResponse({
            'is_following': is_following,
            'followers_count': profile.followers_count()
        })
    
    return JsonResponse({'error': 'Cannot follow yourself'})

def explore(request):
    posts = Post.objects.all().select_related('author').prefetch_related('likes', 'comments')
    
    # Thêm presigned URLs cho posts
    for post in posts:
        post.image_url = post.get_image_presigned_url() if post.image else None
        if hasattr(post.author, 'userprofile'):
            post.author.userprofile.avatar_url = post.author.userprofile.get_avatar_presigned_url() if post.author.userprofile.avatar else None
    
    context = {
        'posts': posts,
    }
    return render(request, 'social/explore.html', context)
