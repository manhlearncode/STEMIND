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
                # Sử dụng AutoGen để tạo nội dung file
                print(f"🤖 Sử dụng AutoGen cho: {user_message}")
                enhanced_system = EnhancedEducationSystem()
                result = enhanced_system.process_request(user_message, str(user_id) if user_id else None, use_autogen=True)
                
                if result['success']:
                    bot_response = result['result']
                    # Thêm thông tin về loại AI được sử dụng
                    intent_display = {
                        'lecture': '📚 AI Agent - Tạo bài giảng',
                        'exercise': '📝 AI Agent - Tạo bài tập', 
                        'test': '📋 AI Agent - Tạo bài kiểm tra',
                        'study': '🧠 AI Agent - Trợ lý học tập',
                    }
                    display_intent = intent_display.get(result['intent'], f"🤖 AI Agent - {result['intent']}")
                    bot_response = f"[{display_intent}]\n\n{bot_response}"
                else:
                    # Fallback về RAG nếu AutoGen thất bại
                    print("⚠️ AutoGen thất bại, fallback về RAG")
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
                        'download_url': f'/chatbot/download-file/{generated_file.id}/'
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
        
        # Loại bỏ các tag AI intent nếu có (ví dụ: [📚 AI Agent - Tạo bài giảng])
        formatted_response = re.sub(r'\[.*?AI Agent.*?\]\n\n', '', formatted_response)
        formatted_response = re.sub(r'\[.*?RAG.*?\]\n\n', '', formatted_response)

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
        
        # Create HTML content với style đơn giản, phù hợp cho in ấn
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_type} - STEMIND AI</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #000;
            background: white;
            margin: 0;
            padding: 40px;
            font-size: 12pt;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #000;
            padding-bottom: 20px;
        }}
        .title {{
            color: #000;
            font-size: 20pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .subtitle {{
            color: #666;
            font-size: 12pt;
            font-style: italic;
        }}
        .content {{
            text-align: justify;
            line-height: 1.8;
        }}
        h1 {{
            color: #000;
            font-size: 18pt;
            font-weight: bold;
            margin: 25px 0 18px 0;
            text-align: center;
            text-transform: uppercase;
            border-bottom: 2px solid #000;
            padding-bottom: 8px;
        }}
        h2 {{
            color: #000;
            font-size: 16pt;
            font-weight: bold;
            margin: 20px 0 15px 0;
            text-transform: uppercase;
        }}
        h3 {{
            color: #000;
            font-size: 14pt;
            font-weight: bold;
            margin: 18px 0 12px 0;
            text-transform: uppercase;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
            display: list-item;
        }}
        /* Đảm bảo list items được hiển thị đúng */
        .content li {{
            margin: 8px 0;
            padding-left: 10px;
            list-style-position: outside;
        }}
        hr {{
            border: none;
            border-top: 1px solid #000;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 10pt;
            border-top: 1px solid #000;
            padding-top: 20px;
        }}
        strong {{
            font-weight: bold;
        }}
        em {{
            font-style: italic;
        }}
        @media print {{
            body {{
                padding: 20px;
                font-size: 11pt;
            }}
            .container {{
                max-width: none;
            }}
            .header {{
                page-break-after: avoid;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">{content_type}</div>
            <div class="subtitle">{user_message}</div>
        </div>
        
        <div class="content">
            {formatted_response}
        </div>
        
        <div class="footer">
            <small>STEMIND cảm ơn bạn đã sử dụng dịch vụ của chúng tôi</small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
<script>
            alert('Nhấn tổ hợp phím Ctrl + P để in ra');
            alert('Nhấn tổ hợp phím Ctrl + S để lưu file');
</script>
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
    """Download file từ chatbot sử dụng S3 presigned URL"""
    try:
        from django.http import HttpResponseRedirect, JsonResponse
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
        
        # Tạo presigned URL từ S3 và redirect
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
            if attachment.is_html():
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
                'is_html': attachment.is_html(),  # Thêm flag để frontend biết
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
        
        # Kiểm tra quyền truy cập
        if not request.user.is_staff and attachment.message.session.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Không có quyền truy cập file này'
            }, status=403)
        
        # Kiểm tra xem có phải HTML file không
        if not attachment.is_html():
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
