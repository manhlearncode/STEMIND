# 🚀 STEMIND - Quick Start Guide

## ⚡ Chạy project trong 5 phút

### 📋 Yêu cầu tối thiểu
- Python 3.8+
- Git
- Internet connection

### 🚀 Bước 1: Clone và cài đặt

```bash
# Clone project
git clone https://github.com/your-username/STEMIND.git
cd STEMIND

# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### ⚙️ Bước 2: Cấu hình nhanh

```bash
# Copy file môi trường
cp env.example .env

# Chỉnh sửa file .env (chỉ cần thay đổi SECRET_KEY)
# Windows
notepad .env

# macOS/Linux
nano .env
```

**Thay đổi trong file `.env`:**
```env
SECRET_KEY=your-random-secret-key-here-12345
```

### 🗄️ Bước 3: Database (SQLite - đơn giản nhất)

```bash
# Không cần cài đặt gì thêm, Django sẽ tự động tạo SQLite database

# Chạy migrations
python manage.py migrate

# Tạo admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: 123456
```

### 🚀 Bước 4: Chạy project

```bash
# Khởi động server
python manage.py runserver

# Mở trình duyệt: http://localhost:8000
# Admin: http://localhost:8000/admin/
```

## 🎯 Tính năng cơ bản để test

### 1. **Đăng ký/Đăng nhập**
- Truy cập: http://localhost:8000/register/
- Tạo tài khoản mới

### 2. **Upload tài liệu**
- Đăng nhập → Upload → Chọn file → Submit

### 3. **Chatbot AI**
- Truy cập: http://localhost:8000/chatbot/
- Gửi tin nhắn để test

### 4. **Social Feed**
- Truy cập: http://localhost:8000/social/feed/
- Tạo post, like, comment

## 🔧 Nâng cấp (Optional)

### Redis (cho caching và Celery)
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Khởi động
redis-server
```

### PostgreSQL (cho production)
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Tạo database
sudo -u postgres psql
CREATE DATABASE stemind_db;
CREATE USER stemind_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE stemind_db TO stemind_user;
\q
```

### Cập nhật .env
```env
DATABASE_URL=postgresql://stemind_user:password@localhost:5432/stemind_db
REDIS_URL=redis://localhost:6379/0
```

## 🚨 Troubleshooting nhanh

### Lỗi "No module named..."
```bash
# Kiểm tra virtual environment
which python
# Kết quả phải là: /path/to/STEMIND/venv/bin/python

# Nếu không, kích hoạt lại
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Lỗi database
```bash
# Xóa database cũ (SQLite)
rm db.sqlite3

# Chạy lại migrations
python manage.py migrate
```

### Lỗi port đã sử dụng
```bash
# Sử dụng port khác
python manage.py runserver 8001

# Hoặc tìm process đang sử dụng port 8000
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000
```

### Lỗi static files
```bash
# Thu thập static files
python manage.py collectstatic

# Hoặc tạo symbolic link (development)
python manage.py collectstatic --link
```

## 📱 Test trên mobile

```bash
# Cho phép truy cập từ mạng local
python manage.py runserver 0.0.0.0:8000

# Tìm IP của máy
# Windows
ipconfig

# macOS/Linux
ifconfig

# Truy cập từ mobile: http://YOUR_IP:8000
```

## 🎉 Hoàn thành!

Bây giờ bạn có thể:
- ✅ Truy cập website: http://localhost:8000
- ✅ Upload/download tài liệu
- ✅ Sử dụng chatbot AI
- ✅ Tương tác social
- ✅ Quản lý qua admin panel

## 📚 Đọc thêm

- [README.md](README.md) - Hướng dẫn chi tiết
- [requirements.txt](requirements.txt) - Dependencies
- [env.example](env.example) - Cấu hình môi trường

## 🆘 Cần giúp đỡ?

- Tạo issue trên GitHub
- Liên hệ: contact@stemind.vn
- Facebook: [STEMIND](https://facebook.com/stemind)

---

**⭐ Nếu hướng dẫn này hữu ích, hãy cho chúng tôi một star! ⭐**
