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
from datetime import datetime
import io
from .models import ChatSession, ChatMessage, FileAttachment
from .services.rag_chatbot_service import RAGChatbotService

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
        
        # Sử dụng RAG chatbot từ Chatbot app
        try:
            rag_service = RAGChatbotService()
            
            if user_id:
                # Sử dụng cả dữ liệu cá nhân và chung
                bot_response = rag_service.answer_question_with_user_context(user_message, str(user_id))
            else:
                # Chỉ sử dụng dữ liệu chung
                bot_response = rag_service.answer_question(user_message)
            
            # Create bot message
            bot_msg = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response
            )
            
            # Check if response contains file creation request
            generated_files = []
            if any(keyword in bot_response.lower() for keyword in ['bài giảng', 'bài tập', 'bài kiểm tra', 'tạo file', 'xuất file']):
                # Simulate file generation (you can replace this with actual file generation logic)
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
                    'type': 'rag_response',
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
        
        # Create HTML content with beautiful styling
        html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_type} - STEMIND AI</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 102, 86, 0.15);
            overflow: hidden;
            border: 2px solid #e8f5f3;
        }}
        .header {{
            background: linear-gradient(135deg, #006056 0%, #008069 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.2"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.4;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }}
        .header .icon {{
            font-size: 3rem;
            margin-bottom: 15px;
            display: block;
            position: relative;
            z-index: 1;
        }}
        .content {{
            padding: 40px;
            background: #fafbfc;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #006056;
            background: white;
            box-shadow: 0 5px 15px rgba(0, 102, 86, 0.08);
            border: 1px solid #e8f5f3;
        }}
        .section h3 {{
            color: #006056;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section h3 i {{
            color: #006056;
        }}
        .user-message {{
            background: linear-gradient(135deg, #f0f9f7 0%, #e8f5f3 100%);
            border-left-color: #006056;
            border: 1px solid #d4edda;
        }}
        .bot-response {{
            background: linear-gradient(135deg, #f8fcfb 0%, #f0f9f7 100%);
            border-left-color: #006056;
            border: 1px solid #d1ecf1;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e8f5f3;
            color: #6c757d;
        }}
        .footer .logo {{
            font-weight: bold;
            color: #006056;
        }}
        .timestamp {{
            background: #e8f5f3;
            padding: 10px 15px;
            border-radius: 25px;
            display: inline-block;
            font-size: 0.9rem;
            color: #006056;
            border: 1px solid #d4edda;
        }}
        .badge {{
            background: linear-gradient(135deg, #006056 0%, #008069 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(0, 102, 86, 0.3);
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border-radius: 0;
                border: none;
            }}
            .header {{
                background: #fff !important;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
                color: #006056;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <i class="{icon_class} icon"></i>
            <h1>{content_type}</h1>
            <div class="badge">STEMIND AI</div>
        </div>
        
        <div class="content">
            <div class="section user-message">
                <h3><i class="fas fa-user"></i> Câu hỏi của bạn</h3>
                <p>{user_message}</p>
            </div>
            
            <div class="section bot-response">
                <h3><i class="fas fa-robot"></i> Nội dung được tạo</h3>
                <div>{bot_response.replace(chr(10), '<br>')}</div>
            </div>
        </div>
        
        <div class="footer">
            <div class="timestamp">
                <i class="fas fa-clock"></i> Được tạo vào: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            </div>
            <br>
            <div class="logo">STEMIND AI Assistant</div>
            <small>Hệ thống trí tuệ nhân tạo giáo dục</small>
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
        
        # Kiểm tra quyền truy cập (chỉ user upload hoặc admin mới được download)
        if not request.user.is_staff and attachment.message.session.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Không có quyền truy cập file này'
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
            if not request.user.is_staff and session.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Không có quyền truy cập session này'
                }, status=403)
            
            attachments = FileAttachment.objects.filter(message__session=session)
        else:
            # Lấy tất cả files của user
            if request.user.is_staff:
                attachments = FileAttachment.objects.all()
            else:
                attachments = FileAttachment.objects.filter(message__session__user=request.user)
        
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
