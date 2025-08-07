# Hệ Thống Điểm STEMIND

## Tổng Quan
Hệ thống điểm được thiết kế để khuyến khích tương tác và đóng góp của người dùng trên platform STEMIND. Người dùng có thể tích điểm thông qua các hoạt động và sử dụng điểm để truy cập nội dung premium.

## Cấu Trúc Models

### 1. UserProfile (đã cập nhật)
```python
class UserProfile(models.Model):
    # ... existing fields ...
    points = models.IntegerField(default=0)  # Điểm hiện tại
    last_daily_points = models.DateField(null=True, blank=True)  # Ngày nhận điểm cuối
```

### 2. PointTransaction
```python
class PointTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField()  # Có thể âm hoặc dương
    description = models.TextField(blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. PointSettings
```python
class PointSettings(models.Model):
    daily_login_points = models.IntegerField(default=10)
    upload_file_points = models.IntegerField(default=20)
    create_post_points = models.IntegerField(default=15)
    like_post_points = models.IntegerField(default=2)
    share_post_points = models.IntegerField(default=5)
    comment_points = models.IntegerField(default=3)
    follow_user_points = models.IntegerField(default=5)
    view_paid_file_cost = models.IntegerField(default=5)
    download_paid_file_cost = models.IntegerField(default=10)
```

## Cách Thức Hoạt Động

### Cộng Điểm (Earning Points):
1. **Điểm hàng ngày**: +10 điểm/ngày (chỉ 1 lần/ngày)
2. **Upload tài liệu**: +20 điểm
3. **Tạo bài viết**: +15 điểm
4. **Like bài viết**: +2 điểm
5. **Comment**: +3 điểm
6. **Follow người dùng**: +5 điểm

### Trừ Điểm (Spending Points):
1. **Xem tài liệu có phí**: -5 điểm
2. **Download tài liệu có phí**: -10 điểm

## Service Layer

### PointService
Chứa tất cả logic xử lý điểm:

```python
# Cộng điểm
PointService.award_points(user, transaction_type, points, description, related_object_id)

# Trừ điểm
PointService.deduct_points(user, transaction_type, points, description, related_object_id)

# Điểm hàng ngày
PointService.check_and_award_daily_points(user)

# Specific handlers
PointService.handle_post_creation(user, post_id)
PointService.handle_like_post(user, post_id)
PointService.handle_comment(user, post_id)
PointService.handle_follow_user(user, followed_user_id)
PointService.handle_file_upload(user, file_id)
PointService.handle_view_paid_file(user, file_id)
PointService.handle_download_paid_file(user, file_id)
```

## Tích Hợp Views

### Social Platform:
- `feed()`: Check daily points, award points for posts
- `like_post()`: Award points for likes
- `add_comment()`: Award points for comments
- `follow_user()`: Award points for following

### File Sharing Platform:
- `upload_file()`: Award points for uploads
- `file_detail()`: Deduct points for viewing paid files
- `download_file()`: Deduct points for downloading paid files

## UI/UX Features

### Header Display:
- Badge hiển thị điểm hiện tại
- Link đến lịch sử điểm

### Points History Page:
- Danh sách tất cả giao dịch điểm
- Pagination
- Filter theo loại giao dịch
- Icons cho từng loại hoạt động

### Templates:
- `templates/social/points_history.html`: Trang lịch sử điểm
- Header cập nhật với points badge

## Management Commands

### Award Daily Points:
```bash
python manage.py award_daily_points
```

Có thể chạy với cron job hàng ngày:
```bash
# Crontab entry (chạy lúc 0:01 mỗi ngày)
1 0 * * * cd /path/to/project && python manage.py award_daily_points
```

## Admin Interface

### PointTransaction Admin:
- View tất cả giao dịch điểm
- Filter theo type, user, date
- Read-only interface

### PointSettings Admin:
- Chỉnh sửa số điểm cho các hoạt động
- Singleton pattern (chỉ 1 setting record)

### UserProfile Admin:
- Hiển thị điểm hiện tại của user

## URLs

```python
# Social Platform URLs
path('points/', views.points_history, name='points_history'),
```

## Security & Validation

1. **Atomic Transactions**: Tất cả point operations sử dụng database transactions
2. **Insufficient Points Check**: Không cho phép điểm âm
3. **Daily Points Limit**: Chỉ 1 lần daily points per ngày
4. **Authorization**: Chỉ authenticated users mới có thể earn/spend points

## Workflow Examples

### User Upload File:
1. User upload file thành công
2. `PointService.handle_file_upload()` được gọi
3. +20 điểm được cộng vào account
4. PointTransaction record được tạo
5. User thấy notification về điểm

### User View Paid File:
1. User click vào paid file
2. `PointService.handle_view_paid_file()` check points
3. Nếu đủ điểm: -5 điểm, cho phép xem
4. Nếu không đủ: Error message, redirect về file list

## Future Enhancements

1. **Point Expiry**: Điểm có thể expire sau thời gian nhất định
2. **Point Packages**: User có thể mua điểm
3. **Referral System**: Điểm cho việc invite bạn bè
4. **Achievement System**: Unlock achievements với điểm
5. **Point Leaderboard**: Top users theo điểm
6. **Point Transfer**: User có thể chuyển điểm cho nhau

## Migration Commands

Sau khi tạo models, chạy:
```bash
python manage.py makemigrations Social_Platform
python manage.py migrate
```

## Testing

Để test hệ thống:
1. Register user mới
2. Login để nhận daily points
3. Upload file để nhận upload points
4. Like/comment posts để nhận interaction points
5. View paid files để test point deduction
6. Check points history page
