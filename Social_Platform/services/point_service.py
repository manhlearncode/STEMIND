from django.utils import timezone
from django.db import transaction
from datetime import date
from ..models import PointTransaction, PointSettings, UserProfile, CustomUser


class PointService:
    """Service để quản lý hệ thống điểm"""
    
    @staticmethod
    def award_points(user, transaction_type, points, description="", related_object_id=None):
        """Cộng điểm cho user"""
        try:
            with transaction.atomic():
                # Tạo transaction record
                PointTransaction.objects.create(
                    user=user,
                    transaction_type=transaction_type,
                    points=points,
                    description=description,
                    related_object_id=related_object_id
                )
                
                # Cập nhật điểm của user
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.points += points
                profile.save()
                
                # Tạo thông báo tiếng Việt đẹp hơn
                transaction_messages = {
                    'upload_file': f'🎉 Chúc mừng! Bạn đã nhận được {points} điểm khi tải lên tài liệu',
                    'create_post': f'🎉 Chúc mừng! Bạn đã nhận được {points} điểm khi tạo bài viết mới',
                    'like_post': f'👍 Bạn đã nhận được {points} điểm khi thích bài viết',
                    'comment': f'💬 Bạn đã nhận được {points} điểm khi bình luận',
                    'follow': f'👥 Bạn đã nhận được {points} điểm khi theo dõi người dùng',
                    'daily_login': f'🌅 Chào buổi sáng! Bạn đã nhận được {points} điểm đăng nhập hàng ngày',
                    'profile_completion': f'✅ Bạn đã nhận được {points} điểm khi hoàn thành hồ sơ'
                }
                
                message = transaction_messages.get(transaction_type, f'Bạn đã nhận được {points} điểm')
                return True, message
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def deduct_points(user, transaction_type, points, description="", related_object_id=None):
        """Trừ điểm của user"""
        try:
            with transaction.atomic():
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Kiểm tra xem user có đủ điểm không
                if profile.points < points:
                    return False, f"❌ Bạn không đủ điểm. Hiện tại bạn có {profile.points} điểm nhưng cần {points} điểm"
                
                # Tạo transaction record (với điểm âm)
                PointTransaction.objects.create(
                    user=user,
                    transaction_type=transaction_type,
                    points=-points,  # Lưu dưới dạng âm
                    description=description,
                    related_object_id=related_object_id
                )
                
                # Trừ điểm
                profile.points -= points
                profile.save()
                
                # Tạo thông báo tiếng Việt đẹp hơn
                transaction_messages = {
                    'view_free_file': f'👁️ Đã trừ {points} điểm khi xem tài liệu miễn phí',
                    'download_free_file': f'📥 Đã trừ {points} điểm khi tải xuống tài liệu miễn phí',
                    'view_file': f'👁️ Đã trừ {points} điểm khi xem tài liệu có phí',
                    'download_file': f'📥 Đã trừ {points} điểm khi tải xuống tài liệu có phí',
                    'unlike_post': f'👎 Đã trừ {points} điểm khi hủy thích bài viết'
                }
                
                message = transaction_messages.get(transaction_type, f'Đã trừ {points} điểm')
                return True, message
        except Exception as e:
            return False, str(e)
    

    
    @staticmethod
    def handle_post_creation(user, post_id):
        """Cộng điểm khi tạo post"""
        settings = PointSettings.get_settings()
        return PointService.award_points(
            user=user,
            transaction_type='create_post',
            points=settings.create_post_points,
            description="Created a new post",
            related_object_id=post_id
        )
    
    @staticmethod
    def handle_like_post(user, post_id):
        """Cộng điểm khi like post"""
        settings = PointSettings.get_settings()
        return PointService.award_points(
            user=user,
            transaction_type='like_post',
            points=settings.like_post_points,
            description="Liked a post",
            related_object_id=post_id
        )
    
    @staticmethod
    def handle_unlike_post(user, post_id):
        """Trừ điểm khi hủy like post"""
        settings = PointSettings.get_settings()
        return PointService.deduct_points(
            user=user,
            transaction_type='unlike_post',
            points=settings.like_post_points,  # Trừ số điểm bằng với số điểm đã cộng khi like
            description="Unliked a post",
            related_object_id=post_id
        )
    
    @staticmethod
    def handle_comment(user, post_id):
        """Cộng điểm khi comment"""
        settings = PointSettings.get_settings()
        return PointService.award_points(
            user=user,
            transaction_type='comment',
            points=settings.comment_points,
            description="Commented on a post",
            related_object_id=post_id
        )
    
    @staticmethod
    def handle_follow_user(user, followed_user_id):
        """Cộng điểm khi follow user"""
        settings = PointSettings.get_settings()
        return PointService.award_points(
            user=user,
            transaction_type='follow',
            points=settings.follow_user_points,
            description="Followed a user",
            related_object_id=followed_user_id
        )
    
    @staticmethod
    def handle_file_upload(user, file_id):
        """Cộng điểm khi upload file"""
        settings = PointSettings.get_settings()
        return PointService.award_points(
            user=user,
            transaction_type='upload_file',
            points=settings.upload_file_points,
            description="Uploaded a file",
            related_object_id=file_id
        )
    
    @staticmethod
    def handle_view_paid_file(user, file_id):
        """Trừ điểm khi xem tài liệu có phí"""
        settings = PointSettings.get_settings()
        current_points = PointService.get_user_points(user)
        
        if current_points < settings.view_paid_file_cost:
            return False, f"Bạn cần ít nhất {settings.view_paid_file_cost} điểm để xem tài liệu này. Hiện tại bạn có {current_points} điểm."
        
        return PointService.deduct_points(
            user=user,
            transaction_type='view_file',
            points=settings.view_paid_file_cost,
            description="Viewed a paid file",
            related_object_id=file_id
        )
    
    @staticmethod
    def handle_download_paid_file(user, file_id):
        """Trừ điểm khi download tài liệu có phí"""
        settings = PointSettings.get_settings()
        current_points = PointService.get_user_points(user)
        
        if current_points < settings.download_paid_file_cost:
            return False, f"Bạn cần ít nhất {settings.download_paid_file_cost} điểm để download tài liệu này. Hiện tại bạn có {current_points} điểm."
        
        return PointService.deduct_points(
            user=user,
            transaction_type='download_file',
            points=settings.download_paid_file_cost,
            description="Downloaded a paid file",
            related_object_id=file_id
        )
    
    @staticmethod
    def handle_view_free_file(user, file_id):
        """Trừ điểm khi xem tài liệu free"""
        settings = PointSettings.get_settings()
        current_points = PointService.get_user_points(user)
        
        if current_points < settings.view_free_file_cost:
            return False, f"Bạn cần ít nhất {settings.view_free_file_cost} điểm để xem tài liệu này. Hiện tại bạn có {current_points} điểm."
        
        return PointService.deduct_points(
            user=user,
            transaction_type='view_free_file',
            points=settings.view_free_file_cost,
            description="Viewed a free file",
            related_object_id=file_id
        )
    
    @staticmethod
    def handle_download_free_file(user, file_id):
        """Trừ điểm khi download tài liệu free"""
        settings = PointSettings.get_settings()
        current_points = PointService.get_user_points(user)
        
        if current_points < settings.download_free_file_cost:
            return False, f"Bạn cần ít nhất {settings.download_free_file_cost} điểm để download tài liệu này. Hiện tại bạn có {current_points} điểm."
        
        return PointService.deduct_points(
            user=user,
            transaction_type='download_free_file',
            points=settings.download_free_file_cost,
            description="Downloaded a free file",
            related_object_id=file_id
        )
    
    @staticmethod
    def get_user_points(user):
        """Lấy điểm hiện tại của user"""
        try:
            profile = UserProfile.objects.get(user=user)
            return profile.points
        except UserProfile.DoesNotExist:
            return 0
    
    @staticmethod
    def get_user_point_history(user, limit=10):
        """Lấy lịch sử điểm của user"""
        return PointTransaction.objects.filter(user=user)[:limit]
