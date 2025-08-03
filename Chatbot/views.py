from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
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
def chatbot_api(request):
    """API endpoint cho RAG chatbot"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', '')
        user_id = data.get('user_id', None)
        
        if not user_message.strip():
            return JsonResponse({
                'success': False,
                'error': 'Message không được để trống'
            })
        
        # Sử dụng RAG chatbot từ Chatbot app
        try:
            rag_service = RAGChatbotService()
            
            if user_id:
                # Sử dụng cả dữ liệu cá nhân và chung
                bot_response = rag_service.answer_question_with_user_context(user_message, str(user_id))
            else:
                # Chỉ sử dụng dữ liệu chung
                bot_response = rag_service.answer_question(user_message)
            
            return JsonResponse({
                'success': True,
                'response': {
                    'text': bot_response,
                    'type': 'rag_response'
                },
                'session_id': session_id
            })
        except Exception as e:
            print(f"Lỗi trong RAG chatbot: {e}")
            
            # Fallback response
            simple_response = f"Xin lỗi, tôi hiện không thể xử lý câu hỏi '{user_message}'. Hệ thống chatbot đang được cập nhật. Vui lòng thử lại sau."
            return JsonResponse({
                'success': True,
                'response': {
                    'text': simple_response,
                    'type': 'simple_response'
                },
                'session_id': session_id
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

def chatbot_page(request):
    """Trang giao diện chatbot"""
    return render(request, 'chatbot.html')
