from django.shortcuts import redirect
from django.urls import reverse
from Social_Platform.models import UserProfile, CustomUser

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Kiểm tra nếu user đã đăng nhập
        if request.user.is_authenticated:
            # Danh sách URL được phép truy cập mà không cần hoàn thiện profile
            allowed_urls = [
                '/basic-info/',
                '/complete-profile/',
                '/auth/logout/',
                '/logout/',
                '/static/',
                '/media/',
                '/admin/',
                '/admin/login/',
            ]
            
            # Kiểm tra xem URL hiện tại có trong danh sách được phép không
            current_path = request.path
            is_allowed = any(current_path.startswith(url) for url in allowed_urls)
            
            if not is_allowed:
                # Kiểm tra xem user đã có đầy đủ thông tin cơ bản chưa
                user = request.user
                # Chỉ kiểm tra các trường bắt buộc trong CustomUser (không kiểm tra bio và avatar)
                if not (user.firstname and user.lastname and user.age and user.role):
                    # Nếu chưa hoàn thiện, chuyển hướng đến trang điền thông tin cơ bản
                    return redirect('basic_info')

        response = self.get_response(request)
        return response 