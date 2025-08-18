# Hướng dẫn cài đặt tính năng Preview HTML và Download PDF

## 🎯 Tính năng mới

Hệ thống chatbot hiện đã được cải tiến với các tính năng sau:

1. **Preview HTML**: User có thể xem trước file HTML bằng cách click vào nút "Xem"
2. **Download PDF**: User có thể download file PDF bằng cách click vào nút "PDF" 
3. **UI cải tiến**: Giao diện hiển thị file với các nút preview và download rõ ràng

## 📋 Yêu cầu hệ thống

### 1. Cài đặt thư viện Python

Chọn **một trong hai** phương án sau:

#### Phương án A: Sử dụng WeasyPrint (Khuyến nghị)
```bash
pip install weasyprint==61.2
```

#### Phương án B: Sử dụng pdfkit + wkhtmltopdf
```bash
pip install pdfkit==1.0.0
```

Và cài đặt wkhtmltopdf:
- **Windows**: Tải về từ https://wkhtmltopdf.org/downloads.html
- **Ubuntu/Debian**: `sudo apt-get install wkhtmltopdf`
- **CentOS/RHEL**: `sudo yum install wkhtmltopdf`
- **macOS**: `brew install wkhtmltopdf`

### 2. Cấu hình URL routing

Thêm URL pattern vào file `urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... các URL khác ...
    path('chatbot/preview-html/<int:file_id>/', views.preview_html_file, name='preview_html_file'),
    path('chatbot/download-file/<int:file_id>/', views.download_chat_file, name='download_chat_file'),
    # ... các URL khác ...
]
```

## 🚀 Cách sử dụng

### 1. Tạo file HTML

User gửi message yêu cầu tạo file, ví dụ:
- "Tôi muốn tạo bài giảng"
- "Tạo bài tập toán cho lớp 3"
- "Tạo bài kiểm tra khoa học"

### 2. Preview file HTML

Sau khi file được tạo, user sẽ thấy:
- **Nút "Xem"** (màu xanh dương): Click để xem preview HTML trong tab mới
- **Nút "PDF"** (màu xanh lá): Click để download file PDF

### 3. Download PDF

Khi user click nút "PDF":
1. Hệ thống sẽ tự động convert HTML thành PDF
2. File PDF được tải xuống với tên tương ứng (ví dụ: `Bai_giang_20231201_143000.pdf`)

## 🔧 Cấu trúc code

### 1. Backend Changes

#### `views.py`
- Cải tiến `download_chat_file()`: Tự động convert HTML to PDF
- Thêm `convert_html_to_pdf_content()`: Function convert HTML thành PDF
- Cập nhật response JSON để include `preview_url` và `is_html`

#### `models.py` 
- Đã có sẵn `preview_html_file()` function để preview HTML

### 2. Frontend Changes

#### `templates/chatbot.html`
- Thêm `previewFile()` function: Mở preview trong tab mới
- Cải tiến UI hiển thị file attachments với 2 nút:
  - Nút "Xem" cho HTML files
  - Nút "PDF"/"Tải" tùy theo loại file
- Cập nhật File Manager với UI mới

## ⚙️ Cấu hình tùy chọn

### 1. Tùy chỉnh PDF output

Trong `convert_html_to_pdf_content()`, bạn có thể tùy chỉnh:

```python
# WeasyPrint options
from weasyprint import HTML, CSS

# pdfkit options  
options = {
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in', 
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
}
```

### 2. Tùy chỉnh HTML template

File HTML được tạo có CSS đẹp mắt với:
- Responsive design
- Print-friendly styles
- Modern UI với gradients và animations

## 🐛 Troubleshooting

### Lỗi WeasyPrint không cài đặt được

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# CentOS/RHEL  
sudo yum install python3-devel python3-pip python3-cffi pango harfbuzz
```

### Lỗi wkhtmltopdf không tìm thấy

Đảm bảo wkhtmltopdf đã được cài đặt và có trong PATH:

```bash
which wkhtmltopdf
# Hoặc
wkhtmltopdf --version
```

### File PDF bị lỗi font

Đảm bảo hệ thống có font tiếng Việt:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu fonts-liberation fonts-noto-cjk
```

## 📝 Notes

1. **Performance**: Việc convert HTML to PDF có thể mất 2-5 giây tùy theo độ phức tạp của file
2. **File size**: PDF file thường lớn hơn HTML file 2-3 lần
3. **Browser compatibility**: Preview HTML hoạt động trên tất cả trình duyệt hiện đại
4. **Security**: Chỉ user đã login mới có thể preview và download file

## 🎉 Hoàn tất!

Sau khi cài đặt xong, hệ thống sẽ có đầy đủ tính năng:
- ✅ Tạo file HTML từ chatbot response
- ✅ Preview HTML trong tab mới  
- ✅ Convert và download PDF tự động
- ✅ UI/UX thân thiện với user
