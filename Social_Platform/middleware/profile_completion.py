from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User
from Social_Platform.models import UserProfile

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra nếu user đã đăng nhập
        if request.user.is_authenticated:
            # Danh sách URL được phép truy cập mà không cần hoàn thiện profile
            allowed_urls = [
                '/complete-profile/',
                '/auth/logout/',
                '/logout/',
                '/static/',
                '/media/',
            ]
            
            # Kiểm tra xem URL hiện tại có trong danh sách được phép không
            current_path = request.path
            is_allowed = any(current_path.startswith(url) for url in allowed_urls)
            
            if not is_allowed:
                try:
                    profile = request.user.userprofile
                    # Kiểm tra xem profile đã được hoàn thiện chưa
                    if not (profile.firstname and profile.lastname and profile.age and profile.role):
                        # Nếu chưa hoàn thiện, chuyển hướng đến trang điều thông tin
                        return redirect('complete_profile')
                except UserProfile.DoesNotExist:
                    # Nếu chưa có profile, chuyển hướng đến trang điều thông tin
                    return redirect('complete_profile')

        response = self.get_response(request)
        return response 