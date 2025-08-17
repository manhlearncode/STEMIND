#!/usr/bin/env python3
"""
Script test để kiểm tra AutoGen system
Chạy: python test_autogen_system.py
"""

import os
import sys

# Thêm đường dẫn hiện tại vào Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_autogen_system():
    """Test AutoGen system"""
    print("🧪 Testing AutoGen System...")
    
    try:
        # Test import
        print("\n1. Testing imports...")
        from Chatbot.services.autogen_education_system import EnhancedEducationSystem
        print("✅ EnhancedEducationSystem imported successfully")
        
        # Test initialization
        print("\n2. Testing initialization...")
        system = EnhancedEducationSystem()
        print("✅ System initialized successfully")
        
        # Test hybrid response
        print("\n3. Testing hybrid response...")
        test_input = "Tạo bài giảng về nguyên tố hóa học"
        result = system.hybrid_response(test_input, user_id="test_user")
        
        print(f"✅ Result received:")
        print(f"   Intent: {result.get('intent')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Source: {result.get('source')}")
        print(f"   Sources: {result.get('sources')}")
        print(f"   Result length: {len(result.get('result', ''))}")
        
        # Test RAG fallback
        print("\n4. Testing RAG fallback...")
        rag_result = system.rag_service.answer_question("Giải thích về nguyên tố hóa học")
        print(f"✅ RAG result length: {len(rag_result)}")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment...")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY: {api_key[:10]}...")
    else:
        print("⚠️ OPENAI_API_KEY not found")
    
    # Check Python path
    print(f"✅ Python path: {sys.path[:3]}...")
    
    # Check current directory
    print(f"✅ Current directory: {os.getcwd()}")
    
    # Check available packages
    try:
        import autogen
        print(f"✅ AutoGen version: {autogen.__version__}")
    except ImportError:
        print("⚠️ AutoGen not available")
    
    try:
        import openai
        print(f"✅ OpenAI version: {openai.__version__}")
    except ImportError:
        print("⚠️ OpenAI not available")

if __name__ == "__main__":
    print("🚀 Starting AutoGen System Test...")
    
    # Test environment first
    test_environment()
    
    # Test system
    success = test_autogen_system()
    
    if success:
        print("\n🎯 System is working correctly!")
    else:
        print("\n💥 System has issues that need to be fixed!")
        sys.exit(1)
