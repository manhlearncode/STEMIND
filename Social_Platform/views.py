from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.db import models
from .models import Post, Like, Comment, UserProfile, CustomUser, PointTransaction
from .forms import PostForm, CommentForm
from .services.point_service import PointService
# Create your views here.

def check_and_award_daily_points(user):
    """Wrapper: use PointService to award daily points safely once/day."""
    return PointService.check_and_award_daily_points(user)

@login_required
def feed(request):
    # Check and award daily points once per day using a dated session key
    from datetime import date
    today_str = date.today().isoformat()
    if request.session.get('daily_points_date') != today_str:
        success, message = check_and_award_daily_points(request.user)
        # Regardless of success, set the date to avoid repeated calls on refresh
        request.session['daily_points_date'] = today_str
        if success and message:
            messages.success(request, message)
    
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
            
            # Award points for creating post
            PointService.handle_post_creation(request.user, post.id)
            
            messages.success(request, 'Post created successfully!')
            return redirect('social:feed')
    else:
        form = PostForm()
    
    # Get user points for display
    user_points = PointService.get_user_points(request.user)
    
    context = {
        'posts': posts,
        'form': form,
        'user_points': user_points,
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
        # Award points for liking post
        PointService.handle_like_post(request.user, post_id)
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.like_count()
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        import json
        try:
            # Try to parse JSON first
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except:
            # Fallback to form data
            content = request.POST.get('content', '').strip()
        
        if content:
            comment = Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
            
            # Award points for commenting
            PointService.handle_comment(request.user, post_id)
            
            # Get user display name
            user_display_name = request.user.get_full_name() or request.user.username
            user_avatar = request.user.username[:1].upper()
            
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'content': comment.content,
                'user': user_display_name,
                'user_avatar': user_avatar,
                'username': request.user.username,
                'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p')
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
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
    import json
    
    print(f"Follow request received - Method: {request.method}, Username: {username}, User: {request.user}")
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        user_to_follow = get_object_or_404(CustomUser, username=username)
        print(f"User to follow found: {user_to_follow}")
        
        if request.user == user_to_follow:
            return JsonResponse({'success': False, 'error': 'Cannot follow yourself'}, status=400)
        
        # Get or create profile for the user being followed
        profile, created = UserProfile.objects.get_or_create(user=user_to_follow)
        print(f"Profile created: {created}, Profile: {profile}")
        
        # Check current follow status
        is_following = profile.followers.filter(id=request.user.id).exists()
        print(f"Current follow status: {is_following}")
        
        if is_following:
            # Unfollow
            profile.followers.remove(request.user)
            is_following = False
            action = 'unfollowed'
            message = f'You unfollowed {user_to_follow.get_full_name() or user_to_follow.username}'
        else:
            # Follow
            profile.followers.add(request.user)
            is_following = True
            action = 'followed'
            message = f'You followed {user_to_follow.get_full_name() or user_to_follow.username}'
            
            # Award points for following user
            PointService.handle_follow_user(request.user, user_to_follow.id)
        
        followers_count = profile.followers_count()
        print(f"New follow status: {is_following}, Followers count: {followers_count}")
        
        response_data = {
            'success': True,
            'is_following': is_following,
            'action': action,
            'followers_count': followers_count,
            'message': message
        }
        
        print(f"Response data: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error in follow_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': f'Server error: {str(e)}'
        }, status=500)


@login_required
def points_history(request):
    """Hiển thị lịch sử điểm của user"""
    transactions = PointTransaction.objects.filter(user=request.user).order_by('-created_at')
    user_points = PointService.get_user_points(request.user)
    
    # Tổng điểm đã cộng và đã trừ
    total_earned = transactions.filter(points__gt=0).aggregate(models.Sum('points'))['points__sum'] or 0
    total_spent = abs(transactions.filter(points__lt=0).aggregate(models.Sum('points'))['points__sum'] or 0)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 20)  # 20 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'user_points': user_points,
        'total_earned': total_earned,
        'total_spent': total_spent,
    }
    return render(request, 'social/points_history.html', context)

@login_required
def check_profile_completion(request):
    """Kiểm tra xem profile đã hoàn thiện chưa"""
    try:
        profile = request.user.userprofile
        is_complete = bool(profile.firstname and profile.lastname and profile.age and profile.role and profile.address)
        return JsonResponse({
            'is_complete': is_complete,
            'profile': {
                'firstname': profile.firstname,
                'lastname': profile.lastname,
                'age': profile.age,
                'role': profile.role,
                'address': profile.address,
                'role_display': profile.get_role_display() if profile.role else None
            }
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'is_complete': False,
            'profile': None
        })

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

@login_required
def followers_list(request, username):
    """Display list of followers for a user"""
    user = get_object_or_404(CustomUser, username=username)
    try:
        profile = user.userprofile
        followers = profile.followers.all().select_related('userprofile')
        
        # Add avatar URLs
        for follower in followers:
            if hasattr(follower, 'userprofile') and follower.userprofile.avatar:
                follower.userprofile.avatar_url = follower.userprofile.get_avatar_presigned_url()
        
        context = {
            'profile_user': user,
            'followers': followers,
            'title': f'Followers of {user.get_full_name() or user.username}'
        }
        return render(request, 'social/followers_list.html', context)
    except UserProfile.DoesNotExist:
        context = {
            'profile_user': user,
            'followers': [],
            'title': f'Followers of {user.get_full_name() or user.username}'
        }
        return render(request, 'social/followers_list.html', context)

@login_required
def following_list(request, username):
    """Display list of users being followed by a user"""
    user = get_object_or_404(CustomUser, username=username)
    
    # Get users that this user is following
    following = CustomUser.objects.filter(
        userprofile__followers=user
    ).select_related('userprofile')
    
    # Add avatar URLs
    for followed_user in following:
        if hasattr(followed_user, 'userprofile') and followed_user.userprofile.avatar:
            followed_user.userprofile.avatar_url = followed_user.userprofile.get_avatar_presigned_url()
    
    context = {
        'profile_user': user,
        'following': following,
        'title': f'Following by {user.get_full_name() or user.username}'
    }
    return render(request, 'social/following_list.html', context)
