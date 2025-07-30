#!/usr/bin/env python3
"""
Script để tạo file .env từ env_file.txt
Usage: python setup_env.py
"""

import os
import shutil
from dotenv import load_dotenv
load_dotenv()

def create_env_file():
    """Tạo file .env từ env_file.txt"""
    try:
        # Kiểm tra file env_file.txt có tồn tại không
        if not os.path.exists('env_file.txt'):
            print("❌ File env_file.txt không tồn tại!")
            return False
        
        # Copy env_file.txt thành .env
        shutil.copy('env_file.txt', '.env')
        print("✅ Đã tạo file .env thành công!")
        print("📝 Nội dung file .env:")
        
        # Hiển thị nội dung file .env
        with open('.env', 'r') as f:
            content = f.read()
            print(content)
        
        print("\n🔒 File .env đã được tạo và sẽ được .gitignore bảo vệ")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo file .env: {str(e)}")
        return False

def check_gitignore():
    """Kiểm tra .gitignore có bảo vệ .env không"""
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .gitignore đã bảo vệ file .env")
                return True
            else:
                print("⚠️  .gitignore chưa bảo vệ file .env")
                return False
    except FileNotFoundError:
        print("❌ File .gitignore không tồn tại!")
        return False

def main():
    """Main function"""
    print("🚀 Setup Environment Variables")
    print("=" * 40)
    
    # Kiểm tra .gitignore
    if not check_gitignore():
        print("❌ Cần cấu hình .gitignore trước!")
        return
    
    # Tạo file .env
    if create_env_file():
        print("\n🎉 Setup hoàn tất!")
        print("💡 Bây giờ bạn có thể:")
        print("   1. Chạy: python manage.py runserver")
        print("   2. Commit code mà không lo lộ secret keys")
        print("   3. Chia sẻ env_example.txt với team")
    else:
        print("\n❌ Setup thất bại!")

if __name__ == "__main__":
    main() 