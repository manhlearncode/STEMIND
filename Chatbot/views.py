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
    """Generate a downloadable file based on chatbot response"""
    try:
        # Determine file type based on user request
        file_type = 'document'
        file_extension = '.txt'
        mime_type = 'text/plain'
        
        if any(keyword in user_message.lower() for keyword in ['bài giảng', 'lesson plan']):
            filename = f"Bai_giang_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            content_type = 'Bài giảng'
        elif any(keyword in user_message.lower() for keyword in ['bài tập', 'exercise']):
            filename = f"Bai_tap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            content_type = 'Bài tập'
        elif any(keyword in user_message.lower() for keyword in ['bài kiểm tra', 'test', 'quiz']):
            filename = f"Bai_kiem_tra_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            content_type = 'Bài kiểm tra'
        else:
            filename = f"Noi_dung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            content_type = 'Nội dung'
        
        # Create file content
        file_content = f"""
{content_type} - Được tạo bởi STEMIND AI
{"="*50}

Câu hỏi của bạn:
{user_message}

{"="*50}

Nội dung được tạo:
{bot_response}

{"="*50}
Được tạo vào: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Tạo bởi: STEMIND AI Assistant
"""
        
        # Create file object
        file_obj = ContentFile(file_content.encode('utf-8'))
        file_obj.name = filename
        
        # Create a bot message for the file
        file_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=f'Đã tạo file: {filename}'
        )
        
        # Create file attachment
        attachment = FileAttachment.objects.create(
            message=file_message,
            file=file_obj,
            original_name=filename,
            file_type=file_type,
            file_size=len(file_content.encode('utf-8')),
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
    """Download file từ chatbot"""
    try:
        from django.http import FileResponse, Http404
        from django.conf import settings
        import os
        
        # Lấy file attachment
        attachment = FileAttachment.objects.get(id=file_id)
        
        # Kiểm tra quyền truy cập (chỉ user upload hoặc admin mới được download)
        if not request.user.is_staff and attachment.message.session.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Không có quyền truy cập file này'
            }, status=403)
        
        # Kiểm tra file có tồn tại không
        if not attachment.file or not os.path.exists(attachment.file.path):
            raise Http404("File không tồn tại")
        
        # Tạo response để download
        response = FileResponse(
            open(attachment.file.path, 'rb'),
            content_type=attachment.mime_type
        )
        
        # Set filename cho download
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_name}"'
        
        return response
        
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
            files_data.append({
                'id': attachment.id,
                'name': attachment.original_name,
                'size': attachment.get_file_size_display(),
                'type': attachment.file_type,
                'mime_type': attachment.mime_type,
                'uploaded_at': attachment.uploaded_at.isoformat(),
                'session_id': attachment.message.session.session_id,
                'session_title': attachment.message.session.title,
                'download_url': f'/chatbot/download-file/{attachment.id}/'
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
