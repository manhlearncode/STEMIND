from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import mimetypes
import re
from datetime import datetime
import io
from .models import ChatSession, ChatMessage, FileAttachment
from .services.rag_chatbot_service import RAGChatbotService
try:
    from .services.autogen_education_system import EnhancedEducationSystem
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("AutoGen not available, using RAG only")

def chatbot_view(request):
    """View chính cho chatbot"""
    if request.method == 'POST':
        message = request.POST.get('message', '')
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Khởi tạo RAG service từ Chatbot app
        rag_service = RAGChatbotService()
        
        if user_id:
            # Sử dụng cả dữ liệu cá nhân và chung
            response = rag_service.answer_question_with_user_context(message, str(user_id))
        else:
            # Chỉ sử dụng dữ liệu chung
            response = rag_service.answer_question(message)
        
        return JsonResponse({'response': response})
    
    return render(request, 'chatbot.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """API endpoint để upload file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Không có file được upload'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        session_id = request.POST.get('session_id', '')
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Validate file size (max 500MB)
        if uploaded_file.size > 500 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'File quá lớn. Kích thước tối đa là 500MB'
            }, status=400)
        
        # Get or create session
        if session_id:
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'user_id': user_id, 'title': 'Chat with Files'}
            )
        else:
            session = ChatSession.objects.create(
                user_id=user_id,
                title='Chat with Files'
            )
            session_id = session.session_id
        
        # Determine file type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Create a temporary message for file attachment (will be replaced when user sends message)
        temp_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=f'[File uploaded: {uploaded_file.name}]'
        )
        
        # Create file attachment
        attachment = FileAttachment.objects.create(
            message=temp_message,
            file=uploaded_file,
            original_name=uploaded_file.name,
            file_type=FileAttachment().get_file_type_from_mime(mime_type),
            file_size=uploaded_file.size,
            mime_type=mime_type
        )
        
        return JsonResponse({
            'success': True,
            'file_id': attachment.id,
            'file_name': attachment.original_name,
            'file_size': attachment.get_file_size_display(),
            'file_type': attachment.file_type,
            'session_id': session_id,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """API endpoint cho RAG chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', '')
        user_id = data.get('user_id', None)
        file_ids = data.get('file_ids', [])  # List of file IDs attached to this message
        
        if not user_message.strip() and not file_ids:
            return JsonResponse({
                'success': False,
                'error': 'Message hoặc file không được để trống'
            })
        
        # Get or create session
        if session_id:
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'user_id': user_id, 'title': 'Chat with Files'}
            )
        else:
            session = ChatSession.objects.create(
                user_id=user_id,
                title='Chat with Files'
            )
            session_id = session.session_id
        
        # Create user message
        user_msg = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=user_message
        )
        
        # Attach files to message if any
        if file_ids:
            attachments = FileAttachment.objects.filter(id__in=file_ids)
            for attachment in attachments:
                # Create a copy of the attachment for this message
                FileAttachment.objects.create(
                    message=user_msg,
                    file=attachment.file,
                    original_name=attachment.original_name,
                    file_type=attachment.file_type,
                    file_size=attachment.file_size,
                    mime_type=attachment.mime_type
                )
                # Delete the temporary message that was created during upload
                if attachment.message.content.startswith('[File uploaded:'):
                    attachment.message.delete()
        
        # Phân biệt giữa sinh file và chat thường
        try:
            # Kiểm tra xem có phải yêu cầu tạo file không
            file_creation_keywords = ['tạo bài giảng', 'tạo bài tập', 'tạo bài kiểm tra', 'tạo đề thi', 'tạo lesson', 'tạo exercise', 'tạo test']
            is_file_creation = any(keyword in user_message.lower() for keyword in file_creation_keywords)
            
            if is_file_creation and AUTOGEN_AVAILABLE:
                # Sử dụng hệ thống hybrid AutoGen + RAG
                print(f"🤖 Sử dụng hệ thống Hybrid cho: {user_message}")
                enhanced_system = EnhancedEducationSystem()
                
                # Sử dụng hybrid response để kết hợp AutoGen và RAG
                result = enhanced_system.hybrid_response(user_message, str(user_id) if user_id else None)
                
                if result['success']:
                    bot_response = result['result']
                    # Thêm thông tin về loại AI được sử dụng
                    intent_display = {
                        'hybrid_lecture': '🤖 Hybrid AI - Bài giảng nâng cao',
                        'hybrid_exercise': '🤖 Hybrid AI - Bài tập nâng cao', 
                        'hybrid_test': '🤖 Hybrid AI - Bài kiểm tra nâng cao',
                        'hybrid_study': '🤖 Hybrid AI - Trợ lý học tập nâng cao',
                        'lecture': '📚 AI Agent - Tạo bài giảng',
                        'exercise': '📝 AI Agent - Tạo bài tập', 
                        'test': '📋 AI Agent - Tạo bài kiểm tra',
                        'study': '🧠 AI Agent - Trợ lý học tập',
                        'rag_only': '🔍 RAG System - Thông tin từ cơ sở dữ liệu',
                    }
                    display_intent = intent_display.get(result['intent'], f"🤖 AI System - {result['intent']}")
                    bot_response = f"[{display_intent}]\n\n{bot_response}"
                else:
                    # Fallback về RAG nếu hybrid thất bại
                    print("⚠️ Hybrid system thất bại, fallback về RAG")
                    rag_service = RAGChatbotService()
                    if user_id:
                        bot_response = rag_service.answer_question_with_user_context(user_message, str(user_id))
                    else:
                        bot_response = rag_service.answer_question(user_message)
                    bot_response = f"[⚠️ RAG Fallback]\n\n{bot_response}"
            else:
                # Sử dụng RAG cho chat thường
                print(f"🔍 Sử dụng RAG cho: {user_message}")
                rag_service = RAGChatbotService()
                
                if user_id:
                    # Sử dụng cả dữ liệu cá nhân và chung
                    bot_response = rag_service.answer_question_with_user_context(user_message, str(user_id))
                else:
                    # Chỉ sử dụng dữ liệu chung
                    bot_response = rag_service.answer_question(user_message)
                        
                bot_response = f"[🔍 RAG Chatbot]\n\n{bot_response}"
            
            # Create bot message
            bot_msg = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response
            )
            
            # Check if response contains file creation request
            generated_files = []
            if is_file_creation:
                # Tạo file từ nội dung AutoGen hoặc RAG
                generated_file = generate_content_file(user_message, bot_response, session)
                if generated_file:
                    generated_files.append({
                        'id': generated_file.id,
                        'name': generated_file.original_name,
                        'size': generated_file.get_file_size_display(),
                        'type': generated_file.file_type,
                        'download_url': f'/chatbot/download-file/{generated_file.id}/',
                        'preview_url': f'/chatbot/preview-html/{generated_file.id}/',
                        'is_html': generated_file.is_html() or (generated_file.file_type == 'document' and generated_file.mime_type == 'text/html')
                    })
            
            return JsonResponse({
                'success': True,
                'response': {
                    'text': bot_response,
                    'type': 'autogen_response' if is_file_creation and AUTOGEN_AVAILABLE else 'rag_response',
                    'files': generated_files
                },
                'session_id': session_id,
                'message_id': user_msg.id
            })
        except Exception as e:
            print(f"Lỗi trong RAG chatbot: {e}")
            
            # Fallback response
            simple_response = f"Xin lỗi, tôi hiện không thể xử lý câu hỏi '{user_message}'. Hệ thống chatbot đang được cập nhật. Vui lòng thử lại sau."
            
            # Create bot message
            bot_msg = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=simple_response
            )
            
            return JsonResponse({
                'success': True,
                'response': {
                    'text': simple_response,
                    'type': 'simple_response'
                },
                'session_id': session_id,
                'message_id': user_msg.id
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def user_profile_view(request):
    """View để xem profile của user"""
    rag_service = RAGChatbotService()
    profile = rag_service.get_user_profile(str(request.user.id))
    
    return JsonResponse(profile or {'error': 'No profile found'})

@login_required
def list_users_view(request):
    """View để liệt kê tất cả users có embeddings (chỉ admin)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'})
    
    rag_service = RAGChatbotService()
    users = rag_service.list_users_with_embeddings()
    
    return JsonResponse({'users': users})

def generate_content_file(user_message, bot_response, session):
    """Generate a downloadable HTML file based on chatbot response"""
    try:
        # Determine file type based on user request
        file_type = 'document'
        file_extension = '.html'
        mime_type = 'text/html'
        
        if any(keyword in user_message.lower() for keyword in ['bài giảng', 'lesson plan']):
            filename = f"Bai_giang_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            content_type = 'Bài giảng'
            icon_class = 'fas fa-chalkboard-teacher'
            color_class = 'primary'
        elif any(keyword in user_message.lower() for keyword in ['bài tập', 'exercise']):
            filename = f"Bai_tap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            content_type = 'Bài tập'
            icon_class = 'fas fa-tasks'
            color_class = 'success'
        elif any(keyword in user_message.lower() for keyword in ['bài kiểm tra', 'test', 'quiz']):
            filename = f"Bai_kiem_tra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            content_type = 'Bài kiểm tra'
            icon_class = 'fas fa-question-circle'
            color_class = 'warning'
        else:
            filename = f"Noi_dung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            content_type = 'Nội dung'
            icon_class = 'fas fa-file-alt'
            color_class = 'info'
        
        # Xử lý markdown để tạo HTML đơn giản, phù hợp cho in ấn
        formatted_response = bot_response
        
        # Loại bỏ các tag AI intent nếu có (ví dụ: [🤖 Hybrid AI - Bài giảng nâng cao])
        formatted_response = re.sub(r'\[.*?AI Agent.*?\]\n\n', '', formatted_response)
        formatted_response = re.sub(r'\[.*?RAG.*?\]\n\n', '', formatted_response)
        formatted_response = re.sub(r'\[.*?Hybrid AI.*?\]\n\n', '', formatted_response)
        formatted_response = re.sub(r'\[.*?AI System.*?\]\n\n', '', formatted_response)

        formatted_response = re.sub(r'#### (.*?)(?=\n|$)', lambda m: f'<h4 style="color: #000; font-size: 14pt; font-weight: bold; margin: 18px 0 12px 0; text-transform: uppercase;">{m.group(1).upper()}</h4>', formatted_response)
        # Xử lý headings ### (H3) - In hoa đầu mục phụ
        formatted_response = re.sub(r'### (.*?)(?=\n|$)', lambda m: f'<h3 style="color: #000; font-size: 14pt; font-weight: bold; margin: 18px 0 12px 0; text-transform: uppercase;">{m.group(1).upper()}</h3>', formatted_response)
        
        # Xử lý headings ## (H2) - In hoa đầu mục chính 
        formatted_response = re.sub(r'## (.*?)(?=\n|$)', lambda m: f'<h2 style="color: #000; font-size: 16pt; font-weight: bold; margin: 20px 0 15px 0; text-transform: uppercase;">{m.group(1).upper()}</h2>', formatted_response)
        
        # Xử lý headings # (H1) - In hoa tiêu đề chính
        formatted_response = re.sub(r'# (.*?)(?=\n|$)', lambda m: f'<h1 style="color: #000; font-size: 18pt; font-weight: bold; margin: 25px 0 18px 0; text-align: center; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 8px;">{m.group(1).upper()}</h1>', formatted_response)
        
        # Xử lý các đầu mục số La Mã (I., II., III., IV., V.) - Cải thiện regex
        formatted_response = re.sub(r'^\s*(I{1,3}V?|IV|V|VI{0,3}|IX|X)\.?\s+(.*?)(?=\n|$)', lambda m: f'<h2 style="color: #000; font-size: 14pt; font-weight: bold; margin: 20px 0 12px 0; text-transform: uppercase;">{m.group(1).upper()}. {m.group(2).upper()}</h2>', formatted_response, flags=re.MULTILINE)
        
        # Xử lý các đầu mục số (1., 2., 3., ...) - Cải thiện regex để xử lý khoảng trắng
        formatted_response = re.sub(r'^\s*(\d+)\.?\s+(.*?)(?=\n|$)', lambda m: f'<h3 style="color: #000; font-size: 12pt; font-weight: bold; margin: 15px 0 10px 0; text-transform: uppercase;">{m.group(1)}. {m.group(2).upper()}</h3>', formatted_response, flags=re.MULTILINE)
        
        # Xử lý các đầu mục có dấu gạch đầu dòng (-) - Thêm format này
        formatted_response = re.sub(r'^\s*-\s+(.*?)(?=\n|$)', lambda m: f'<li style="margin: 8px 0; padding-left: 10px; list-style-type: disc;">{m.group(1)}</li>', formatted_response, flags=re.MULTILINE)
        
        # Xử lý các đầu mục có dấu chấm (•) - Thêm format này
        formatted_response = re.sub(r'^\s*•\s+(.*?)(?=\n|$)', lambda m: f'<li style="margin: 8px 0; padding-left: 10px; list-style-type: circle;">{m.group(1)}</li>', formatted_response, flags=re.MULTILINE)
        
        # Bọc các list items trong ul tags
        formatted_response = re.sub(r'(<li.*?</li>)(?=\s*<li|$)', r'<ul>\1</ul>', formatted_response, flags=re.DOTALL)
        
        # Xử lý dấu gạch ngang
        formatted_response = formatted_response.replace('---', '<hr style="border: none; border-top: 1px solid #000; margin: 20px 0;">')
        
        # Xử lý xuống dòng
        formatted_response = formatted_response.replace('\n', '<br>')
        
        # Create HTML content với style đẹp mắt và màu sắc hấp dẫn
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_type} - STEMIND AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Merriweather:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #006056;
            --secondary-color: #00897B;
            --accent-color: #26A69A;
            --text-dark: #2c3e50;
            --text-light: #7f8c8d;
            --background-light: #f8f9fa;
            --border-color: #e9ecef;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --info-color: #3498db;
        }}

        body {{
            font-family: 'Roboto', sans-serif;
            line-height: 1.7;
            color: var(--text-dark);
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 30px;
            font-size: 14pt;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 96, 86, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            text-align: center;
            padding: 40px 30px;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="50" r="0.5" fill="white" opacity="0.05"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }}
        
        .title {{
            font-family: 'Merriweather', serif;
            font-size: 28pt;
            font-weight: 700;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 1;
        }}
        
        .subtitle {{
            font-size: 14pt;
            opacity: 0.9;
            font-weight: 300;
            position: relative;
            z-index: 1;
        }}
        
        .content {{
            padding: 50px 40px;
            text-align: justify;
            line-height: 1.8;
            background: white;
        }}
        
        h1 {{
            font-family: 'Merriweather', serif;
            color: var(--primary-color);
            font-size: 22pt;
            font-weight: 700;
            margin: 30px 0 20px 0;
            text-align: center;
            text-transform: uppercase;
            border-bottom: 3px solid var(--accent-color);
            padding-bottom: 15px;
            position: relative;
        }}
        
        h1::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 2px;
        }}
        
        h2 {{
            color: var(--secondary-color);
            font-size: 18pt;
            font-weight: 600;
            margin: 25px 0 18px 0;
            text-transform: uppercase;
            border-left: 5px solid var(--accent-color);
            padding-left: 20px;
            background: linear-gradient(90deg, rgba(38, 166, 154, 0.1) 0%, transparent 100%);
            padding: 12px 20px;
            border-radius: 5px;
        }}
        
        h3 {{
            color: var(--primary-color);
            font-size: 16pt;
            font-weight: 500;
            margin: 20px 0 15px 0;
            text-transform: uppercase;
            position: relative;
            padding-left: 25px;
        }}
        
        h3::before {{
            content: '●';
            color: var(--accent-color);
            font-size: 20pt;
            position: absolute;
            left: 0;
            top: -2px;
        }}
        
        h4 {{
            color: var(--text-dark);
            font-size: 14pt;
            font-weight: 500;
            margin: 18px 0 12px 0;
            text-transform: uppercase;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 5px;
        }}
        
        ul, ol {{
            margin: 20px 0;
            padding-left: 0;
        }}
        
        li {{
            margin: 12px 0;
            padding: 8px 15px;
            background: rgba(38, 166, 154, 0.05);
            border-left: 3px solid var(--accent-color);
            border-radius: 5px;
            list-style: none;
            position: relative;
            transition: all 0.3s ease;
        }}
        
        li::before {{
            content: '▸';
            color: var(--accent-color);
            font-weight: bold;
            margin-right: 10px;
        }}
        
        li:hover {{
            background: rgba(38, 166, 154, 0.1);
            transform: translateX(5px);
        }}
        
        .content > ul > li,
        .content > ol > li {{
            margin: 12px 0;
            padding: 10px 20px;
            background: linear-gradient(90deg, rgba(0, 96, 86, 0.05) 0%, transparent 100%);
            border-left: 4px solid var(--primary-color);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 96, 86, 0.1);
        }}
        
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            margin: 30px 0;
            border-radius: 1px;
        }}
        
        .footer {{
            background: var(--background-light);
            margin-top: 0;
            text-align: center;
            color: var(--text-light);
            font-size: 12pt;
            padding: 30px;
            border-top: 3px solid var(--primary-color);
            position: relative;
        }}
        
        .footer::before {{
            content: '';
            position: absolute;
            top: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-color), var(--secondary-color));
        }}
        
        strong {{
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        em {{
            font-style: italic;
            color: var(--secondary-color);
        }}
        
        /* Highlight boxes cho nội dung quan trọng */
        .highlight-box {{
            background: linear-gradient(135deg, rgba(0, 96, 86, 0.1) 0%, rgba(38, 166, 154, 0.05) 100%);
            border: 2px solid var(--accent-color);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0, 96, 86, 0.1);
        }}
        
        /* Animation cho khi load trang */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .content {{
            animation: fadeInUp 0.8s ease-out;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
                font-size: 11pt;
            }}
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
            .header {{
                background: var(--primary-color) !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }}
            .header::before {{
                display: none;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }}
            li {{
                page-break-inside: avoid;
            }}
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 15px;
                font-size: 12pt;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .title {{
                font-size: 22pt;
            }}
            h1 {{
                font-size: 18pt;
            }}
            h2 {{
                font-size: 16pt;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">{content_type}</div>
        </div>
        
        <div class="content">
            {formatted_response}
        </div>
        
        <div class="footer">
            <strong>🌟 STEMIND AI Assistant</strong><br>
        </div>
    </div>
    # <script>
    #     // Chỉ hiển thị alert khi không phải in
    #     if (!window.location.search.includes('print')) {{
    #         setTimeout(() => {{
    #             if (confirm('Bạn muốn in tài liệu này ngay không?')) {{
    #                 window.print();
    #             }}
    #         }}, 1000);
    #     }}
    # </script>
</body>
</html>"""
        
        # Create file object
        file_obj = ContentFile(html_content.encode('utf-8'))
        file_obj.name = filename
        
        # Create a bot message for the file
        file_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=f'Đã tạo file HTML: {filename}'
        )
        
        # Create file attachment
        attachment = FileAttachment.objects.create(
            message=file_message,
            file=file_obj,
            original_name=filename,
            file_type=file_type,
            file_size=len(html_content.encode('utf-8')),
            mime_type=mime_type
        )
        
        return attachment
        
    except Exception as e:
        print(f"Error generating file: {e}")
        return None

def chatbot_page(request):
    """Trang giao diện chatbot"""
    return render(request, 'chatbot.html')

@login_required
def download_chat_file(request, file_id):
    """Download file từ chatbot - Convert HTML to PDF nếu cần"""
    try:
        from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
        from django.conf import settings
        
        # Lấy file attachment
        attachment = FileAttachment.objects.get(id=file_id)
        
        # Kiểm tra quyền truy cập - Cho phép tất cả user đã đăng nhập download file
        session = attachment.message.session
        
        # Admin có thể truy cập tất cả files
        if request.user.is_staff:
            pass
        # User đã đăng nhập có thể download file
        elif request.user.is_authenticated:
            pass
        else:
            return JsonResponse({
                'success': False,
                'error': 'Cần đăng nhập để download file'
            }, status=403)
        
        # Nếu là HTML file, convert thành PDF
        if attachment.mime_type == 'text/html' and attachment.file_type == 'document':
            try:
                # Đọc nội dung HTML
                if hasattr(attachment.file, 'read'):
                    attachment.file.seek(0)
                    html_content = attachment.file.read().decode('utf-8')
                    
                    # Sử dụng FileExportService để convert HTML to PDF
                    from .services.file_export_service import FileExportService
                    export_service = FileExportService()
                    
                    # Tạo tên file PDF
                    pdf_filename = attachment.original_name.replace('.html', '.pdf')
                    
                    # Convert HTML to PDF content
                    pdf_content = convert_html_to_pdf_content(html_content, pdf_filename)
                    
                    if pdf_content:
                        # Trả về PDF file
                        response = HttpResponse(pdf_content, content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
                        return response
                    else:
                        # Fallback về HTML nếu convert PDF thất bại
                        pass
                        
            except Exception as e:
                print(f"Error converting HTML to PDF: {e}")
                # Fallback về HTML file gốc
                pass
        
        # Tạo presigned URL từ S3 và redirect cho các file khác
        presigned_url = attachment.get_presigned_url()
        if presigned_url:
            return HttpResponseRedirect(presigned_url)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Không thể tạo download link'
            }, status=500)
        
    except FileAttachment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File không tồn tại'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def convert_html_to_pdf_content(html_content, filename):
    """Convert HTML content to PDF bytes

    Ưu tiên dùng Playwright (Chromium) nếu có; fallback sang WeasyPrint, rồi pdfkit.
    """
    # 1) Thử dùng Playwright (Chromium headless)
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            # Render trực tiếp HTML string
            page.set_content(html_content, wait_until="load")
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0.75in", "right": "0.75in", "bottom": "0.75in", "left": "0.75in"},
            )
            context.close()
            browser.close()
            return pdf_bytes
    except Exception as e:
        print(f"Playwright PDF failed: {e}")

    # 2) Fallback: WeasyPrint
    try:
        import weasyprint
        from io import BytesIO

        pdf_file = BytesIO()
        weasyprint.HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        return pdf_file.getvalue()
    except Exception as e:
        print(f"WeasyPrint failed: {e}")

    # 3) Fallback: pdfkit (wkhtmltopdf)
    try:
        import pdfkit

        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None,
        }
        return pdfkit.from_string(html_content, False, options=options)
    except Exception as e:
        print(f"pdfkit failed: {e}")
        return None

@login_required
def list_chat_files(request, session_id=None):
    """Liệt kê files trong chat session"""
    try:
        if session_id:
            # Lấy files của session cụ thể
            session = ChatSession.objects.get(session_id=session_id)
            
            # Cho phép tất cả user đã đăng nhập xem files
            pass
            
            attachments = FileAttachment.objects.filter(message__session=session)
        else:
            # Lấy tất cả files - Cho phép user thường xem tất cả files
            if request.user.is_staff:
                attachments = FileAttachment.objects.all()
            else:
                # User thường có thể xem tất cả files
                attachments = FileAttachment.objects.all()
        
        files_data = []
        for attachment in attachments:
            # Tạo presigned URL cho mỗi file
            download_url = attachment.get_presigned_url()
            
            # Thêm preview URL cho HTML files
            preview_url = None
            if attachment.is_html() or (attachment.file_type == 'document' and attachment.mime_type == 'text/html'):
                preview_url = f'/chatbot/preview-html/{attachment.id}/'
            
            files_data.append({
                'id': attachment.id,
                'name': attachment.original_name,
                'size': attachment.get_file_size_display(),
                'type': attachment.file_type,
                'mime_type': attachment.mime_type,
                'uploaded_at': attachment.uploaded_at.isoformat(),
                'session_id': attachment.message.session.session_id,
                'session_title': attachment.message.session.title,
                'download_url': download_url,
                'file_url': download_url,  # Thêm file_url để tương thích
                'preview_url': preview_url,  # Thêm preview URL cho HTML files
                                        'is_html': attachment.is_html() or (attachment.file_type == 'document' and attachment.mime_type == 'text/html'),  # Thêm flag để frontend biết
            })
        
        return JsonResponse({
            'success': True,
            'files': files_data
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session không tồn tại'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def test_download(request, file_id):
    """Test view để kiểm tra presigned URL"""
    try:
        attachment = FileAttachment.objects.get(id=file_id)
        
        # Kiểm tra quyền truy cập
        if not request.user.is_staff and attachment.message.session.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Không có quyền truy cập file này'
            }, status=403)
        
        # Tạo presigned URL
        presigned_url = attachment.get_presigned_url()
        
        return JsonResponse({
            'success': True,
            'file_info': {
                'id': attachment.id,
                'name': attachment.original_name,
                'size': attachment.get_file_size_display(),
                'type': attachment.file_type,
                'mime_type': attachment.mime_type,
                'presigned_url': presigned_url,
                'file_path': attachment.file.name if attachment.file else None
            }
        })
        
    except FileAttachment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File không tồn tại'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def preview_html_file(request, file_id):
    """Preview HTML file trực tiếp trong browser"""
    try:
        from django.http import HttpResponse
        
        # Lấy file attachment
        attachment = FileAttachment.objects.get(id=file_id)
        
        # Cho phép mọi user đã đăng nhập preview (đã có @login_required)
        # Nếu muốn hạn chế theo session owner thì có thể bổ sung kiểm tra tại đây
        
        # Kiểm tra xem có phải HTML file không
        if not (attachment.is_html() or (attachment.file_type == 'document' and attachment.mime_type == 'text/html')):
            return JsonResponse({
                'success': False,
                'error': 'Chỉ có thể preview HTML files'
            }, status=400)
        
        # Đọc nội dung file
        if hasattr(attachment.file, 'read'):
            attachment.file.seek(0)
            html_content = attachment.file.read().decode('utf-8')
            
            # Trả về HTML content
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'inline; filename="{attachment.original_name}"'
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': 'Không thể đọc file'
            }, status=500)
        
    except FileAttachment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File không tồn tại'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
