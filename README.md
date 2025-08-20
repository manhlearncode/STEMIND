# 🚀 STEMIND - Nền tảng chia sẻ tài liệu giáo dục STEM

[![Django](https://img.shields.io/badge/Django-5.2.3+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

STEMIND là nền tảng chia sẻ tài liệu giáo dục STEM hàng đầu Việt Nam, kết nối giáo viên và học sinh trong việc học tập và nghiên cứu khoa học.

## 🌟 Tính năng chính

- 📚 **Quản lý tài liệu**: Upload, download và chia sẻ tài liệu giáo dục
- 🤖 **Trợ lý AI**: Chatbot thông minh hỗ trợ học tập
- 👥 **Mạng xã hội**: Kết nối giáo viên và học sinh
- 🎯 **Hệ thống điểm**: Tích lũy điểm thưởng cho hoạt động
- 🔍 **Tìm kiếm nâng cao**: Tìm kiếm tài liệu theo nhiều tiêu chí
- 📱 **Responsive Design**: Tương thích mọi thiết bị

## 🛠️ Công nghệ sử dụng

- Backend: Python 3.8+, Django 5.2.x, python-dotenv
- AI/RAG: OpenAI (`openai`), LangChain OpenAI (`langchain-openai`), NumPy (`numpy`), scikit-learn
- Lưu trữ tệp & media: AWS S3 (`boto3`, `django-storages`), Pillow
- Xuất PDF: Playwright (Chromium)
- Cơ sở dữ liệu: SQLite (mặc định dự án)
- Frontend: HTML5, CSS3, JavaScript; Bootstrap 5 (CDN), Font Awesome (CDN), SweetAlert2 (CDN)
- Triển khai (production): Gunicorn (Linux)

## 📋 Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **Node.js**: 16.0 hoặc cao hơn (cho frontend build)
- **Database**: PostgreSQL 12+ hoặc MySQL 8.0+
- **Redis**: 6.0+ (cho caching và Celery)
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🚀 Hướng dẫn cài đặt

### 1. Clone repository

```bash
# Clone repository chính
git clone https://github.com/your-username/STEMIND.git

# Di chuyển vào thư mục project
cd STEMIND

# Kiểm tra branch hiện tại
git branch -a
```

### 2. Tạo virtual environment

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Kiểm tra Python version
python --version
```

### 3. Cài đặt dependencies

```bash
# Cập nhật pip
pip install --upgrade pip

# Cài đặt tất cả dependencies
pip install -r requirements.txt

# Kiểm tra cài đặt
pip list
```

### 3.1. Cài đặt trình duyệt cho Playwright (bắt buộc cho chức năng xuất PDF)

```bash
# Windows/macOS/Linux
python -m playwright install chromium

# (Linux thường) Cài thêm system deps nếu thiếu
# python -m playwright install-deps
```

### 4. Cấu hình môi trường

```bash
# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa file .env với thông tin của bạn
# Windows
notepad .env

# macOS/Linux
nano .env
```

**Nội dung file `.env`:**
```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stemind_db
# Hoặc MySQL
# DATABASE_URL=mysql://user:password@localhost:3306/stemind_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (nếu sử dụng)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# OpenAI (cho chatbot)
OPENAI_API_KEY=your-openai-api-key

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe (cho payment)
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### 5. Cài đặt và cấu hình database

#### PostgreSQL (Khuyến nghị)
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows: Tải từ https://www.postgresql.org/download/windows/

# Tạo database và user
sudo -u postgres psql
CREATE DATABASE stemind_db;
CREATE USER stemind_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE stemind_db TO stemind_user;
\q
```

#### MySQL
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS
brew install mysql

# Windows: Tải từ https://dev.mysql.com/downloads/mysql/

# Tạo database và user
mysql -u root -p
CREATE DATABASE stemind_db;
CREATE USER 'stemind_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON stemind_db.* TO 'stemind_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Cài đặt Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows: Tải từ https://redis.io/download

# Khởi động Redis
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS
brew services start redis

# Kiểm tra Redis
redis-cli ping
# Kết quả: PONG
```

### 7. Chạy migrations

```bash
# Tạo migrations
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Kiểm tra database
python manage.py showmigrations
```

### 8. Tạo superuser

```bash
# Tạo tài khoản admin
python manage.py createsuperuser

# Nhập thông tin:
# Username: admin
# Email: admin@stemind.vn
# Password: ********
# Password (again): ********
```

### 9. Thu thập static files

```bash
# Thu thập static files
python manage.py collectstatic

# Tạo symbolic link (development)
python manage.py collectstatic --link
```

### 10. Khởi động server

```bash
# Khởi động Django server
python manage.py runserver

# Hoặc chỉ định port
python manage.py runserver 8000

# Hoặc cho phép truy cập từ mạng
python manage.py runserver 0.0.0.0:8000
```

### 11. Huấn luyện Embeddings cho Chatbot (tùy chọn nhưng khuyến nghị)

```bash
# Tạo embeddings chung từ dữ liệu (files, posts, comments)
python manage.py train_rag_chatbot --embeddings-file stem_embeddings.json

# Tạo embeddings cá nhân cho một user cụ thể
python manage.py train_rag_chatbot --user-id <USER_ID>

# Tạo embeddings cho tất cả users
python manage.py train_rag_chatbot --all-users
```

Khai báo biến môi trường `OPENAI_API_KEY` trong file `.env` trước khi chạy.

## 🌐 Truy cập ứng dụng

- **Website chính**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin/
- **API docs**: http://localhost:8000/api/
- **Chatbot**: http://localhost:8000/chatbot/

## 🔧 Cấu hình nâng cao

### Celery (Background Tasks)

```bash
# Terminal 1: Khởi động Redis
redis-server

# Terminal 2: Khởi động Celery worker
celery -A The_Chalk worker -l info

# Terminal 3: Khởi động Celery beat (scheduled tasks)
celery -A The_Chalk beat -l info

# Terminal 4: Django server
python manage.py runserver
```

### Elasticsearch (Search Engine)

```bash
# Ubuntu/Debian
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update
sudo apt install elasticsearch

# Khởi động Elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch

# Kiểm tra
curl -X GET "localhost:9200"
```

### Production Deployment

```bash
# Cài đặt Gunicorn
pip install gunicorn

# Khởi động với Gunicorn
gunicorn The_Chalk.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Sử dụng systemd service
sudo nano /etc/systemd/system/stemind.service
```

**Nội dung file service:**
```ini
[Unit]
Description=STEMIND Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/STEMIND
Environment="PATH=/path/to/STEMIND/venv/bin"
ExecStart=/path/to/STEMIND/venv/bin/gunicorn --workers 4 --bind unix:/path/to/STEMIND/stemind.sock The_Chalk.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🧪 Testing

```bash
# Chạy tất cả tests
python manage.py test

# Chạy tests với coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Chạy tests cụ thể
python manage.py test Chatbot.tests
python manage.py test Social_Platform.tests
python manage.py test File_sharing_platform.tests
```

## 📊 Monitoring

```bash
# Django Debug Toolbar (development)
# Thêm vào INSTALLED_APPS và MIDDLEWARE

# Django Silk (performance profiling)
# Truy cập: http://localhost:8000/silk/

# Prometheus metrics
# Truy cập: http://localhost:8000/metrics/
```

## 🚨 Troubleshooting

### Lỗi thường gặp

#### 1. Database connection error
```bash
# Kiểm tra database service
sudo systemctl status postgresql
sudo systemctl status mysql

# Kiểm tra connection
python manage.py dbshell
```

#### 2. Redis connection error
```bash
# Kiểm tra Redis service
sudo systemctl status redis-server

# Kiểm tra connection
redis-cli ping
```

#### 3. Static files không hiển thị
```bash
# Thu thập static files
python manage.py collectstatic

# Kiểm tra DEBUG setting
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
```

#### 4. Migration errors
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Hoặc reset hoàn toàn
python manage.py migrate zero
python manage.py migrate
```

#### 5. Permission errors
```bash
# Sửa quyền thư mục
sudo chown -R $USER:$USER /path/to/STEMIND
chmod -R 755 /path/to/STEMIND

# Sửa quyền database
sudo -u postgres psql
ALTER USER stemind_user CREATEDB;
```

## 📚 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Dự án này được cấp phép theo MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 📞 Liên hệ

- **Website**: https://stemind.vn
- **Email**: contact@stemind.vn
- **Facebook**: [STEMIND](https://facebook.com/stemind)
- **Zalo**: [STEMIND Support](https://zalo.me/stemind)

## 🙏 Lời cảm ơn

Cảm ơn tất cả contributors đã đóng góp vào dự án STEMIND!

---

**⭐ Nếu dự án này hữu ích, hãy cho chúng tôi một star! ⭐**
