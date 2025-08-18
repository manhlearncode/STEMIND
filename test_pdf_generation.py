#!/usr/bin/env python3
"""
Script test tính năng convert HTML to PDF
Chạy script này để test xem thư viện PDF có hoạt động không
"""

def test_weasyprint():
    """Test WeasyPrint library"""
    try:
        import weasyprint
        from io import BytesIO
        
        print("✅ WeasyPrint đã được cài đặt")
        
        # Test convert HTML to PDF
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test PDF</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #006065; }
            </style>
        </head>
        <body>
            <h1>Test PDF Generation</h1>
            <p>Đây là test file để kiểm tra việc convert HTML thành PDF.</p>
            <p>Nếu bạn thấy file PDF được tạo thành công, nghĩa là hệ thống hoạt động tốt!</p>
        </body>
        </html>
        """
        
        pdf_file = BytesIO()
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        # Lưu file test
        with open('test_weasyprint.pdf', 'wb') as f:
            f.write(pdf_file.getvalue())
            
        print("✅ WeasyPrint test thành công! File test_weasyprint.pdf đã được tạo.")
        return True
        
    except ImportError:
        print("❌ WeasyPrint chưa được cài đặt")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi test WeasyPrint: {e}")
        return False

def test_pdfkit():
    """Test pdfkit library"""
    try:
        import pdfkit
        
        print("✅ pdfkit đã được cài đặt")
        
        # Test convert HTML to PDF
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test PDF</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #006065; }
            </style>
        </head>
        <body>
            <h1>Test PDF Generation</h1>
            <p>Đây là test file để kiểm tra việc convert HTML thành PDF.</p>
            <p>Nếu bạn thấy file PDF được tạo thành công, nghĩa là hệ thống hoạt động tốt!</p>
        </body>
        </html>
        """
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
        }
        
        pdf_content = pdfkit.from_string(html_content, False, options=options)
        
        # Lưu file test
        with open('test_pdfkit.pdf', 'wb') as f:
            f.write(pdf_content)
            
        print("✅ pdfkit test thành công! File test_pdfkit.pdf đã được tạo.")
        return True
        
    except ImportError:
        print("❌ pdfkit chưa được cài đặt")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi test pdfkit: {e}")
        print("💡 Gợi ý: Đảm bảo wkhtmltopdf đã được cài đặt và có trong PATH")
        return False

def main():
    """Main test function"""
    print("🔍 Bắt đầu test các thư viện PDF...")
    print("=" * 50)
    
    weasyprint_ok = test_weasyprint()
    print("-" * 30)
    pdfkit_ok = test_pdfkit()
    
    print("=" * 50)
    print("📊 Kết quả test:")
    
    if weasyprint_ok:
        print("✅ WeasyPrint: Hoạt động tốt (Khuyến nghị sử dụng)")
    else:
        print("❌ WeasyPrint: Không hoạt động")
        
    if pdfkit_ok:
        print("✅ pdfkit: Hoạt động tốt")
    else:
        print("❌ pdfkit: Không hoạt động")
        
    if weasyprint_ok or pdfkit_ok:
        print("\n🎉 Hệ thống PDF conversion sẵn sàng sử dụng!")
    else:
        print("\n⚠️  Cần cài đặt ít nhất một thư viện PDF:")
        print("   - pip install weasyprint (Khuyến nghị)")
        print("   - pip install pdfkit + cài đặt wkhtmltopdf")

if __name__ == "__main__":
    main()
