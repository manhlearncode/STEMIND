import asyncio
import os
from typing import List, Dict, Any, Optional
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import openai
from dotenv import load_dotenv

# Import existing services
from .rag_chatbot_service import RAGChatbotService
from .user_embedding_service import UserEmbeddingService

load_dotenv()


class EducationalMultiAgentSystem:
    """
    Hệ thống đa agent cho giáo dục STEM sử dụng Microsoft AutoGen
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Khởi tạo các service hiện có
        self.rag_service = RAGChatbotService()
        self.user_embedding_service = UserEmbeddingService()
        
        # Cấu hình LLM
        self.llm_config = {
            "config_list": [{
                "model": "gpt-4.1-mini",  # hoặc gpt-3.5-turbo để tiết kiệm
                "api_key": self.api_key,
                "temperature": 0.7
            }],
            "timeout": 120,
        }
        
        # Khởi tạo các agent
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Khởi tạo tất cả các agent chuyên biệt"""
        
        # 1. Agent Quản lý (Coordinator)
        self.coordinator = AssistantAgent(
            name="Coordinator",
            system_message="""Bạn là điều phối viên chính của hệ thống giáo dục STEM.
            Nhiệm vụ:
            - Phân tích yêu cầu của người dùng
            - Quyết định agent nào phù hợp nhất để xử lý
            - Điều phối luồng công việc giữa các agent
            - Tổng hợp kết quả cuối cùng
            
            Các tác vụ có thể: tạo bài giảng, tạo bài tập, tạo bài kiểm tra, học tập/nghiên cứu
            """,
            llm_config=self.llm_config
        )
        
        # 2. Agent Tạo Bài Giảng
        self.lecture_agent = AssistantAgent(
            name="LectureCreator",
            system_message="""Bạn là chuyên gia tạo bài giảng STEM.
            Chuyên môn:
            - Thiết kế nội dung bài giảng có cấu trúc
            - Tạo slides thuyết trình
            - Xây dựng ví dụ minh họa
            - Đề xuất hoạt động tương tác
            
            Format bài giảng chuẩn:
            1. Mục tiêu học tập
            2. Kiến thức cần thiết
            3. Nội dung chính (có ví dụ)
            4. Hoạt động thực hành
            5. Tóm tắt và đánh giá
            """,
            llm_config=self.llm_config
        )
        
        # 3. Agent Tạo Bài Tập
        self.exercise_agent = AssistantAgent(
            name="ExerciseCreator", 
            system_message="""Bạn là chuyên gia tạo bài tập STEM.
            Chuyên môn:
            - Thiết kế bài tập theo từng cấp độ (dễ, trung bình, khó)
            - Tạo đáp án chi tiết với lời giải
            - Đề xuất phương pháp giải khác nhau
            - Tạo bài tập thực hành và ứng dụng
            
            Cấu trúc bài tập:
            1. Đề bài rõ ràng
            2. Gợi ý (nếu cần)
            3. Lời giải từng bước
            4. Kiến thức liên quan
            5. Bài tập mở rộng
            """,
            llm_config=self.llm_config
        )
        
        # 4. Agent Tạo Bài Kiểm Tra
        self.test_agent = AssistantAgent(
            name="TestCreator",
            system_message="""Bạn là chuyên gia tạo bài kiểm tra STEM.
            Chuyên môn:
            - Thiết kế đề kiểm tra chuẩn
            - Tạo câu hỏi trắc nghiệm và tự luận
            - Xây dựng thang điểm hợp lý
            - Đề xuất tiêu chí đánh giá
            
            Cấu trúc bài kiểm tra:
            1. Thông tin đề thi (thời gian, điểm)
            2. Câu hỏi trắc nghiệm
            3. Câu hỏi tự luận
            4. Đáp án và thang điểm
            5. Ma trận đề kiểm tra
            """,
            llm_config=self.llm_config
        )
        
        # 5. Agent Học Tập/Nghiên Cứu
        self.study_agent = RetrieveAssistantAgent(
            name="StudyAssistant",
            system_message="""Bạn là trợ lý học tập STEM thông minh.
            Chuyên môn:
            - Trả lời câu hỏi học thuật
            - Giải thích khái niệm phức tạp
            - Đề xuất tài liệu tham khảo
            - Hướng dẫn phương pháp học
            
            Phong cách:
            - Giải thích đơn giản, dễ hiểu
            - Sử dụng ví dụ thực tế
            - Khuyến khích tư duy phê phán
            """,
            llm_config=self.llm_config
        )
        
        # 6. Human Proxy Agent
        self.user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",  # Hoặc "TERMINATE" nếu cần xác nhận
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )

    def _get_user_context(self, user_id: str, query: str) -> str:
        """Lấy context từ dữ liệu người dùng"""
        try:
            user_chunks = self.user_embedding_service.get_user_context(user_id, query, top_k=3)
            global_chunks = self.rag_service.get_global_context(query, top_k=3)
            
            all_context = user_chunks + global_chunks
            if all_context:
                return "\n".join(all_context)
            return ""
        except Exception as e:
            print(f"Lỗi khi lấy context: {e}")
            return ""

    def create_lecture(self, topic: str, user_id: str = None, level: str = "intermediate") -> str:
        """Tạo bài giảng"""
        try:
            context = ""
            if user_id:
                context = self._get_user_context(user_id, topic)
            
            prompt = f"""
            Tạo bài giảng về chủ đề: {topic}
            Cấp độ: {level}
            
            Context từ tài liệu:
            {context}
            
            Yêu cầu: Tạo bài giảng đầy đủ, có cấu trúc và dễ hiểu.
            """
            
            # Bắt đầu cuộc hội thoại
            self.user_proxy.initiate_chat(
                self.lecture_agent,
                message=prompt
            )
            
            # Lấy kết quả từ lịch sử chat
            chat_history = self.user_proxy.chat_messages[self.lecture_agent]
            return chat_history[-1]['content'] if chat_history else "Không thể tạo bài giảng"
            
        except Exception as e:
            return f"Lỗi khi tạo bài giảng: {str(e)}"

    def create_exercises(self, topic: str, user_id: str = None, difficulty: str = "mixed") -> str:
        """Tạo bài tập"""
        try:
            context = ""
            if user_id:
                context = self._get_user_context(user_id, topic)
            
            prompt = f"""
            Tạo bài tập về chủ đề: {topic}
            Độ khó: {difficulty}
            
            Context từ tài liệu:
            {context}
            
            Yêu cầu: Tạo ít nhất 5 bài tập với đáp án chi tiết.
            """
            
            self.user_proxy.initiate_chat(
                self.exercise_agent,
                message=prompt
            )
            
            chat_history = self.user_proxy.chat_messages[self.exercise_agent]
            return chat_history[-1]['content'] if chat_history else "Không thể tạo bài tập"
            
        except Exception as e:
            return f"Lỗi khi tạo bài tập: {str(e)}"

    def create_test(self, topic: str, user_id: str = None, test_type: str = "mixed") -> str:
        """Tạo bài kiểm tra"""
        try:
            context = ""
            if user_id:
                context = self._get_user_context(user_id, topic)
            
            prompt = f"""
            Tạo bài kiểm tra về chủ đề: {topic}
            Loại đề: {test_type} (trắc nghiệm/tự luận/mixed)
            
            Context từ tài liệu:
            {context}
            
            Yêu cầu: Tạo đề kiểm tra 60 phút với đáp án và thang điểm.
            """
            
            self.user_proxy.initiate_chat(
                self.test_agent,
                message=prompt
            )
            
            chat_history = self.user_proxy.chat_messages[self.test_agent]
            return chat_history[-1]['content'] if chat_history else "Không thể tạo bài kiểm tra"
            
        except Exception as e:
            return f"Lỗi khi tạo bài kiểm tra: {str(e)}"

    def study_assistant(self, question: str, user_id: str = None) -> str:
        """Trợ lý học tập"""
        try:
            context = ""
            if user_id:
                context = self._get_user_context(user_id, question)
            
            prompt = f"""
            Câu hỏi: {question}
            
            Context từ tài liệu:
            {context}
            
            Hãy trả lời câu hỏi một cách chi tiết và dễ hiểu.
            """
            
            self.user_proxy.initiate_chat(
                self.study_agent,
                message=prompt
            )
            
            chat_history = self.user_proxy.chat_messages[self.study_agent]
            return chat_history[-1]['content'] if chat_history else "Không thể trả lời câu hỏi"
            
        except Exception as e:
            return f"Lỗi khi xử lý câu hỏi: {str(e)}"

    def group_collaboration(self, task: str, user_id: str = None) -> str:
        """
        Sử dụng nhiều agent cùng làm việc cho tác vụ phức tạp
        """
        try:
            context = ""
            if user_id:
                context = self._get_user_context(user_id, task)
            
            # Tạo GroupChat với nhiều agent
            groupchat = GroupChat(
                agents=[self.coordinator, self.lecture_agent, self.exercise_agent, self.test_agent],
                messages=[],
                max_round=10
            )
            
            manager = GroupChatManager(
                groupchat=groupchat,
                llm_config=self.llm_config
            )
            
            prompt = f"""
            Tác vụ: {task}
            
            Context:
            {context}
            
            Hãy phân công và thực hiện tác vụ này một cách hiệu quả nhất.
            """
            
            self.user_proxy.initiate_chat(
                manager,
                message=prompt
            )
            
            # Tổng hợp kết quả
            chat_history = self.user_proxy.chat_messages[manager]
            return chat_history[-1]['content'] if chat_history else "Không thể hoàn thành tác vụ"
            
        except Exception as e:
            return f"Lỗi trong group collaboration: {str(e)}"

    def smart_route_request(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """
        Định tuyến thông minh yêu cầu của người dùng
        """
        try:
            # Phân tích ý định người dùng
            intent_keywords = {
                "lecture": ["bài giảng", "giảng dạy", "thuyết trình", "slide", "lesson"],
                "exercise": ["bài tập", "luyện tập", "thực hành", "exercise", "problem"],
                "test": ["kiểm tra", "bài kiểm tra", "đề thi", "test", "exam"],
                "study": ["giải thích", "là gì", "tại sao", "như thế nào", "help", "hỗ trợ"]
            }
            
            user_input_lower = user_input.lower()
            detected_intent = "study"  # default
            
            for intent, keywords in intent_keywords.items():
                if any(keyword in user_input_lower for keyword in keywords):
                    detected_intent = intent
                    break
            
            # Thực hiện theo ý định được phát hiện
            result = ""
            if detected_intent == "lecture":
                result = self.create_lecture(user_input, user_id)
            elif detected_intent == "exercise":
                result = self.create_exercises(user_input, user_id)
            elif detected_intent == "test":
                result = self.create_test(user_input, user_id)
            else:
                result = self.study_assistant(user_input, user_id)
            
            return {
                "intent": detected_intent,
                "result": result,
                "success": True
            }
            
        except Exception as e:
            return {
                "intent": "unknown",
                "result": f"Lỗi: {str(e)}",
                "success": False
            }


# Wrapper class để tích hợp với hệ thống hiện có
class EnhancedEducationSystem:
    """
    Lớp wrapper để tích hợp AutoGen với hệ thống RAG hiện có
    """
    
    def __init__(self):
        self.autogen_system = EducationalMultiAgentSystem()
        self.rag_service = RAGChatbotService()  # Sử dụng RAG service chính
        
    def process_request(self, user_input: str, user_id: str = None, use_autogen: bool = True):
        """
        Xử lý yêu cầu với tùy chọn sử dụng AutoGen hoặc RAG truyền thống
        """
        try:
            if use_autogen:
                # Sử dụng AutoGen cho các tác vụ tạo nội dung
                autogen_result = self.autogen_system.smart_route_request(user_input, user_id)
                
                # Nếu AutoGen thành công, bổ sung thông tin từ RAG
                if autogen_result['success']:
                    # Lấy context từ RAG để làm phong phú nội dung
                    rag_context = self._get_rag_context(user_input, user_id)
                    if rag_context:
                        enhanced_result = autogen_result['result'] + f"\n\n---\n\n**Thông tin bổ sung từ hệ thống:**\n{rag_context}"
                        autogen_result['result'] = enhanced_result
                        autogen_result['intent'] = f"{autogen_result['intent']}_enhanced"
                
                return autogen_result
            else:
                # Sử dụng RAG cho chat thường
                if user_id:
                    result = self.rag_service.answer_question_with_user_context(user_input, user_id)
                else:
                    result = self.rag_service.answer_question(user_input)
                    
                return {
                    "intent": "rag_chat",
                    "result": result,
                    "success": True
                }
        except Exception as e:
            print(f"AutoGen error: {e}, falling back to RAG")
            # Nếu AutoGen lỗi, fallback về RAG
            try:
                if user_id:
                    result = self.rag_service.answer_question_with_user_context(user_input, user_id)
                else:
                    result = self.rag_service.answer_question(user_input)
                    
                return {
                    "intent": "fallback_rag", 
                    "result": result,
                    "success": True
                }
            except Exception as fallback_error:
                return {
                    "intent": "error",
                    "result": f"Lỗi hệ thống: {str(fallback_error)}",
                    "success": False
                }
    
    def _get_rag_context(self, user_input: str, user_id: str = None) -> str:
        """
        Lấy context từ RAG service để bổ sung cho AutoGen
        """
        try:
            if user_id:
                context = self.rag_service.answer_question_with_user_context(user_input, user_id)
            else:
                context = self.rag_service.answer_question(user_input)
            
            # Giới hạn độ dài context để tránh quá dài
            if len(context) > 500:
                context = context[:500] + "..."
            
            return context
        except Exception as e:
            print(f"Error getting RAG context: {e}")
            return ""
    
    def hybrid_response(self, user_input: str, user_id: str = None) -> dict:
        """
        Tạo response kết hợp giữa AutoGen và RAG
        """
        try:
            # Lấy response từ AutoGen
            autogen_result = self.autogen_system.smart_route_request(user_input, user_id)
            
            # Lấy context từ RAG
            rag_context = self._get_rag_context(user_input, user_id)
            
            # Kết hợp cả hai
            if autogen_result['success'] and rag_context:
                combined_result = f"{autogen_result['result']}\n\n---\n\n**Thông tin bổ sung:**\n{rag_context}"
                return {
                    "intent": f"hybrid_{autogen_result['intent']}",
                    "result": combined_result,
                    "success": True,
                    "sources": ["autogen", "rag"]
                }
            elif autogen_result['success']:
                return autogen_result
            else:
                # Fallback về RAG
                return {
                    "intent": "rag_only",
                    "result": rag_context,
                    "success": True,
                    "sources": ["rag"]
                }
        except Exception as e:
            return {
                "intent": "error",
                "result": f"Lỗi hệ thống hybrid: {str(e)}",
                "success": False
            }


# Ví dụ sử dụng
if __name__ == "__main__":
    # Khởi tạo hệ thống
    education_system = EnhancedEducationSystem()
    
    # Test các chức năng
    test_cases = [
        "Tôi muốn tạo bài giảng về đạo hàm",
        "Cho tôi một số bài tập về tích phân",
        "Tạo đề kiểm tra về hình học không gian",
        "Giải thích định lý Pytago"
    ]
    
    for test in test_cases:
        print(f"\nInput: {test}")
        result = education_system.process_request(test, user_id="test_user")
        print(f"Intent: {result['intent']}")
        print(f"Result: {result['result'][:200]}...")  # Chỉ in 200 ký tự đầu