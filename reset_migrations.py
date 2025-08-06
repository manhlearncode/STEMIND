#!/usr/bin/env python
"""
Script để reset migrations cho Social_Platform
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Chalk.settings')
django.setup()

def reset_migrations():
    """Reset migrations cho Social_Platform"""
    print("Đang reset migrations cho Social_Platform...")
    
    # Xóa tất cả migration files trừ __init__.py và 0001_initial.py
    migration_dir = "Social_Platform/migrations"
    for filename in os.listdir(migration_dir):
        if filename.startswith("0002") or filename.startswith("0003"):
            filepath = os.path.join(migration_dir, filename)
            os.remove(filepath)
            print(f"Đã xóa: {filename}")
    
    # Tạo migration mới
    print("Đang tạo migration mới...")
    execute_from_command_line(['manage.py', 'makemigrations', 'Social_Platform'])
    
    # Chạy migration
    print("Đang chạy migration...")
    execute_from_command_line(['manage.py', 'migrate', 'Social_Platform'])
    
    print("Hoàn tất!")

if __name__ == "__main__":
    reset_migrations() 