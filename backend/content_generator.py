import json
import os
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import datetime
import re

# Khởi tạo OpenAI client
client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-xvI5gYSbiDQ3c4blptwn0A"
)

class ContentGenerator:
    def __init__(self):
        self.templates_file = "./database/email_templates.json"
        self.ensure_templates_file()
        self.load_templates()
    
    def ensure_templates_file(self):
        """Đảm bảo file templates tồn tại"""
        os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
        if not os.path.exists(self.templates_file):
            default_templates = {
                "welcome_email": {
                    "subject_template": "Chào mừng {employee_name} đến với {company_name}!",
                    "body_template": """
Chào {employee_name},

Chúng tôi rất vui mừng chào đón bạn gia nhập đội ngũ {company_name} với vai trò {position}!

Thông tin cơ bản:
- Ngày bắt đầu: {start_date}
- Phòng ban: {department}
- Người quản lý trực tiếp: {manager_name}
- Email công ty: {company_email}

Trong những ngày đầu tiên, bạn sẽ:
1. Tham gia buổi orientation về văn hóa công ty
2. Được cấp các tài khoản và thiết bị cần thiết
3. Gặp gỡ các đồng nghiệp trong team
4. Bắt đầu chương trình onboarding cá nhân hóa

Nếu có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với HR hoặc manager của bạn.

Chúc bạn có những trải nghiệm tuyệt vời tại {company_name}!

Trân trọng,
Đội ngũ HR
{company_name}
                    """,
                    "variables": ["employee_name", "company_name", "position", "start_date", "department", "manager_name", "company_email"]
                },
                "reminder_email": {
                    "subject_template": "Nhắc nhở: Hoàn thành các bước onboarding",
                    "body_template": """
Chào {employee_name},

Hy vọng bạn đang có những ngày đầu tiên tuyệt vời tại {company_name}!

Chúng tôi muốn nhắc nhở bạn về một số bước onboarding cần hoàn thành:

{pending_tasks}

Vui lòng hoàn thành các bước này trước {deadline} để đảm bảo quá trình onboarding diễn ra suôn sẻ.

Nếu cần hỗ trợ, hãy liên hệ với chúng tôi.

Trân trọng,
Đội ngũ HR
                    """,
                    "variables": ["employee_name", "company_name", "pending_tasks", "deadline"]
                }
            }
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(default_templates, f, ensure_ascii=False, indent=2)
    
    def load_templates(self):
        """Tải templates từ file"""
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
    
    def generate_welcome_email(self, employee_info: Dict) -> Dict[str, str]:
        """Tạo email chào mừng tự động"""
        
        # Lấy template cơ bản
        template = self.templates["welcome_email"]
        
        # Chuẩn bị thông tin mặc định
        default_info = {
            "employee_name": "Nhân viên mới",
            "company_name": "Công ty",
            "position": "Vị trí",
            "start_date": datetime.now().strftime("%d/%m/%Y"),
            "department": "Phòng ban",
            "manager_name": "Quản lý",
            "company_email": "email@company.com"
        }
        
        # Cập nhật với thông tin thực tế
        default_info.update(employee_info)
        
        # Tạo prompt cho AI để cá nhân hóa email
        prompt = f"""
Tạo một email chào mừng chuyên nghiệp và thân thiện cho nhân viên mới với thông tin sau:

Tên: {default_info['employee_name']}
Công ty: {default_info['company_name']}
Vị trí: {default_info['position']}
Ngày bắt đầu: {default_info['start_date']}
Phòng ban: {default_info['department']}
Quản lý: {default_info['manager_name']}

Yêu cầu:
1. Tone thân thiện, chuyên nghiệp
2. Bao gồm thông tin cần thiết cho ngày đầu tiên
3. Đề cập đến lộ trình onboarding
4. Khuyến khích liên hệ nếu có thắc mắc
5. Độ dài khoảng 200-300 từ

Trả về format JSON với "subject" và "body".
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Thử parse JSON từ response
            try:
                email_data = json.loads(content)
                return {
                    "subject": email_data.get("subject", f"Chào mừng {default_info['employee_name']} đến với {default_info['company_name']}!"),
                    "body": email_data.get("body", content)
                }
            except json.JSONDecodeError:
                # Nếu không parse được JSON, sử dụng template cơ bản
                subject = template["subject_template"].format(**default_info)
                body = template["body_template"].format(**default_info)
                return {"subject": subject, "body": body}
                
        except Exception as e:
            # Fallback về template cơ bản
            subject = template["subject_template"].format(**default_info)
            body = template["body_template"].format(**default_info)
            return {"subject": subject, "body": body}
    
    def generate_reminder_email(self, employee_name: str, company_name: str, 
                              pending_tasks: List[str], deadline: str = None) -> Dict[str, str]:
        """Tạo email nhắc nhở hoàn thành onboarding"""
        
        if not deadline:
            deadline = "cuối tuần này"
        
        tasks_text = "\n".join([f"- {task}" for task in pending_tasks])
        
        prompt = f"""
Tạo email nhắc nhở nhẹ nhàng và hỗ trợ cho nhân viên về việc hoàn thành các bước onboarding:

Tên nhân viên: {employee_name}
Công ty: {company_name}
Deadline: {deadline}

Các task cần hoàn thành:
{tasks_text}

Yêu cầu:
1. Tone nhẹ nhàng, không áp lực
2. Khuyến khích và hỗ trợ
3. Đề cập rõ deadline
4. Cung cấp cách liên hệ để được hỗ trợ

Trả về format JSON với "subject" và "body".
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            try:
                email_data = json.loads(content)
                return {
                    "subject": email_data.get("subject", "Nhắc nhở: Hoàn thành các bước onboarding"),
                    "body": email_data.get("body", content)
                }
            except json.JSONDecodeError:
                return {"subject": "Nhắc nhở: Hoàn thành các bước onboarding", "body": content}
                
        except Exception as e:
            # Fallback
            template = self.templates["reminder_email"]
            subject = template["subject_template"]
            body = template["body_template"].format(
                employee_name=employee_name,
                company_name=company_name,
                pending_tasks=tasks_text,
                deadline=deadline
            )
            return {"subject": subject, "body": body}
    
    def summarize_document(self, document_text: str, summary_type: str = "general") -> str:
        """Tóm tắt tài liệu"""
        
        # Giới hạn độ dài input
        max_chars = 8000
        if len(document_text) > max_chars:
            document_text = document_text[:max_chars] + "..."
        
        if summary_type == "key_points":
            prompt = f"""
Tóm tắt tài liệu sau thành các điểm chính (key points):

{document_text}

Yêu cầu:
1. Liệt kê 5-10 điểm chính quan trọng nhất
2. Mỗi điểm ngắn gọn, dễ hiểu
3. Sắp xếp theo thứ tự ưu tiên
4. Sử dụng bullet points
5. Tập trung vào thông tin thực tế và hành động cần thiết

Trả lời bằng tiếng Việt.
"""
        elif summary_type == "action_items":
            prompt = f"""
Từ tài liệu sau, hãy trích xuất các hành động cần thực hiện:

{document_text}

Yêu cầu:
1. Liệt kê các bước/hành động cụ thể
2. Sắp xếp theo thứ tự thực hiện
3. Đề cập deadline nếu có
4. Phân loại theo mức độ ưu tiên
5. Format dễ đọc và thực hiện

Trả lời bằng tiếng Việt.
"""
        else:  # general summary
            prompt = f"""
Tóm tắt tài liệu sau một cách ngắn gọn và toàn diện:

{document_text}

Yêu cầu:
1. Tóm tắt trong 150-200 từ
2. Bao gồm ý chính và thông tin quan trọng
3. Dễ hiểu cho người mới
4. Tập trung vào thông tin thực tế
5. Cấu trúc rõ ràng

Trả lời bằng tiếng Việt.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Lỗi khi tóm tắt tài liệu: {e}"
    
    def generate_training_questions(self, content: str, question_type: str = "mixed", 
                                  num_questions: int = 5) -> List[Dict]:
        """Sinh câu hỏi đào tạo từ nội dung"""
        
        # Giới hạn độ dài input
        max_chars = 6000
        if len(content) > max_chars:
            content = content[:max_chars] + "..."
        
        if question_type == "multiple_choice":
            prompt = f"""
Từ nội dung sau, tạo {num_questions} câu hỏi trắc nghiệm (multiple choice):

{content}

Yêu cầu cho mỗi câu hỏi:
1. Câu hỏi rõ ràng, cụ thể
2. 4 lựa chọn A, B, C, D
3. Chỉ có 1 đáp án đúng
4. Các lựa chọn sai hợp lý, không quá dễ loại trừ
5. Tập trung vào kiến thức quan trọng

Format trả về:
```json
[
  {{
    "question": "Câu hỏi...",
    "options": {{
      "A": "Lựa chọn A",
      "B": "Lựa chọn B", 
      "C": "Lựa chọn C",
      "D": "Lựa chọn D"
    }},
    "correct_answer": "A",
    "explanation": "Giải thích tại sao đáp án này đúng"
  }}
]
```

Trả lời bằng tiếng Việt.
"""
        elif question_type == "true_false":
            prompt = f"""
Từ nội dung sau, tạo {num_questions} câu hỏi đúng/sai:

{content}

Yêu cầu:
1. Câu hỏi rõ ràng, không mơ hồ
2. Dựa trên thông tin cụ thể trong nội dung
3. Cân bằng giữa câu đúng và sai
4. Tránh câu hỏi quá dễ đoán

Format trả về:
```json
[
  {{
    "question": "Câu hỏi...",
    "answer": true/false,
    "explanation": "Giải thích"
  }}
]
```

Trả lời bằng tiếng Việt.
"""
        else:  # mixed
            prompt = f"""
Từ nội dung sau, tạo {num_questions} câu hỏi đào tạo đa dạng (trắc nghiệm, đúng/sai, tự luận ngắn):

{content}

Yêu cầu:
1. Đa dạng loại câu hỏi
2. Kiểm tra hiểu biết ở nhiều mức độ
3. Tập trung vào thông tin quan trọng
4. Câu hỏi thực tế, ứng dụng được

Format trả về:
```json
[
  {{
    "type": "multiple_choice/true_false/short_answer",
    "question": "Câu hỏi...",
    "answer": "Đáp án hoặc gợi ý",
    "explanation": "Giải thích"
  }}
]
```

Trả lời bằng tiếng Việt.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.7
            )
            
            content_response = response.choices[0].message.content
            
            # Tìm và parse JSON từ response
            json_match = re.search(r'```json\s*(.*?)\s*```', content_response, re.DOTALL)
            if json_match:
                try:
                    questions = json.loads(json_match.group(1))
                    return questions
                except json.JSONDecodeError:
                    pass
            
            # Nếu không parse được JSON, thử parse toàn bộ response
            try:
                questions = json.loads(content_response)
                return questions
            except json.JSONDecodeError:
                # Fallback: tạo câu hỏi đơn giản
                return [{
                    "type": "short_answer",
                    "question": "Hãy tóm tắt những điểm chính từ tài liệu này.",
                    "answer": "Tham khảo nội dung tài liệu để trả lời",
                    "explanation": "Câu hỏi tổng hợp kiến thức"
                }]
                
        except Exception as e:
            return [{
                "type": "error",
                "question": f"Lỗi khi tạo câu hỏi: {e}",
                "answer": "",
                "explanation": ""
            }]
    
    def generate_onboarding_checklist(self, position: str, department: str = "") -> List[Dict]:
        """Tạo checklist onboarding tự động"""
        
        prompt = f"""
Tạo checklist onboarding chi tiết cho vị trí {position} {f"thuộc phòng {department}" if department else ""}:

Yêu cầu:
1. Chia theo timeline (ngày 1, tuần 1, tháng 1, etc.)
2. Bao gồm cả administrative tasks và job-specific tasks
3. Có người chịu trách nhiệm cho mỗi task
4. Ước tính thời gian hoàn thành
5. Mức độ ưu tiên

Format trả về:
```json
[
  {{
    "timeline": "Ngày 1",
    "tasks": [
      {{
        "task": "Mô tả công việc",
        "responsible": "HR/Manager/IT/etc.",
        "estimated_time": "30 phút",
        "priority": "High/Medium/Low",
        "description": "Chi tiết thêm nếu cần"
      }}
    ]
  }}
]
```

Trả lời bằng tiếng Việt.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.6
            )
            
            content_response = response.choices[0].message.content
            
            # Parse JSON từ response
            json_match = re.search(r'```json\s*(.*?)\s*```', content_response, re.DOTALL)
            if json_match:
                try:
                    checklist = json.loads(json_match.group(1))
                    return checklist
                except json.JSONDecodeError:
                    pass
            
            # Fallback checklist
            return [{
                "timeline": "Ngày 1",
                "tasks": [{
                    "task": "Orientation và giới thiệu công ty",
                    "responsible": "HR",
                    "estimated_time": "2 giờ",
                    "priority": "High",
                    "description": "Tìm hiểu về văn hóa, giá trị và cấu trúc công ty"
                }]
            }]
            
        except Exception as e:
            return [{
                "timeline": "Error",
                "tasks": [{
                    "task": f"Lỗi khi tạo checklist: {e}",
                    "responsible": "System",
                    "estimated_time": "N/A",
                    "priority": "High",
                    "description": "Vui lòng thử lại"
                }]
            }]

# Khởi tạo instance global
content_generator = ContentGenerator()

