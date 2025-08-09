import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

# Khởi tạo OpenAI client
client = OpenAI(
    base_url="https://aiportalapi.stu-platform.live/jpe",
    api_key="sk-xvI5gYSbiDQ3c4blptwn0A"
)

class PersonalizedRoadmap:
    def __init__(self):
        self.data_file = "./database/roadmap_data.json"
        self.ensure_data_file()
        self.load_data()
    
    def ensure_data_file(self):
        """Đảm bảo file dữ liệu tồn tại"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            default_data = {
                "positions": {
                    "developer": {
                        "name": "Lập trình viên",
                        "documents": [
                            "Hướng dẫn coding standards",
                            "Git workflow và best practices",
                            "Tài liệu API documentation",
                            "Security guidelines cho developers"
                        ],
                        "courses": [
                            "Khóa học Clean Code",
                            "Design Patterns trong thực tế",
                            "Testing và TDD",
                            "DevOps cơ bản"
                        ],
                        "timeline": "4 tuần",
                        "milestones": [
                            "Tuần 1: Làm quen với môi trường và tools",
                            "Tuần 2: Học coding standards và Git workflow",
                            "Tuần 3: Thực hành với dự án nhỏ",
                            "Tuần 4: Review code và feedback"
                        ]
                    },
                    "designer": {
                        "name": "Thiết kế UI/UX",
                        "documents": [
                            "Design system và brand guidelines",
                            "User research methodology",
                            "Accessibility standards",
                            "Design tools và workflows"
                        ],
                        "courses": [
                            "Figma advanced techniques",
                            "User Experience Design",
                            "Design thinking workshop",
                            "Prototyping và testing"
                        ],
                        "timeline": "3 tuần",
                        "milestones": [
                            "Tuần 1: Làm quen với design system",
                            "Tuần 2: Thực hành với dự án thực tế",
                            "Tuần 3: Present và nhận feedback"
                        ]
                    },
                    "marketing": {
                        "name": "Marketing",
                        "documents": [
                            "Brand guidelines và messaging",
                            "Marketing strategy overview",
                            "Social media guidelines",
                            "Analytics và reporting tools"
                        ],
                        "courses": [
                            "Digital Marketing fundamentals",
                            "Content Marketing strategy",
                            "SEO và SEM basics",
                            "Marketing automation"
                        ],
                        "timeline": "3 tuần",
                        "milestones": [
                            "Tuần 1: Hiểu về brand và target audience",
                            "Tuần 2: Tạo content plan đầu tiên",
                            "Tuần 3: Launch campaign nhỏ và đo lường"
                        ]
                    },
                    "hr": {
                        "name": "Nhân sự",
                        "documents": [
                            "Quy chế lao động",
                            "Quy trình tuyển dụng",
                            "Performance management",
                            "Employee handbook"
                        ],
                        "courses": [
                            "HR fundamentals",
                            "Recruitment best practices",
                            "Employee engagement",
                            "Labor law updates"
                        ],
                        "timeline": "2 tuần",
                        "milestones": [
                            "Tuần 1: Nắm vững quy trình và chính sách",
                            "Tuần 2: Thực hành với case studies"
                        ]
                    },
                    "sales": {
                        "name": "Kinh doanh",
                        "documents": [
                            "Sales process và methodology",
                            "Product knowledge base",
                            "Customer personas",
                            "CRM system guide"
                        ],
                        "courses": [
                            "Sales fundamentals",
                            "Negotiation skills",
                            "Customer relationship management",
                            "Product training"
                        ],
                        "timeline": "4 tuần",
                        "milestones": [
                            "Tuần 1: Học về sản phẩm và khách hàng",
                            "Tuần 2: Shadowing senior sales",
                            "Tuần 3: Thực hành sales calls",
                            "Tuần 4: Độc lập handle prospects"
                        ]
                    }
                },
                "general_onboarding": {
                    "documents": [
                        "Company handbook",
                        "Organizational chart",
                        "IT security policies",
                        "Benefits và compensation"
                    ],
                    "courses": [
                        "Company culture orientation",
                        "IT security training",
                        "Communication tools training",
                        "Workplace safety"
                    ]
                }
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """Tải dữ liệu từ file"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def save_data(self):
        """Lưu dữ liệu vào file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_available_positions(self) -> List[str]:
        """Lấy danh sách các vị trí có sẵn"""
        return list(self.data["positions"].keys())
    
    def get_roadmap_for_position(self, position: str) -> Optional[Dict]:
        """Lấy lộ trình cho vị trí cụ thể"""
        position_lower = position.lower()
        
        # Tìm kiếm chính xác
        if position_lower in self.data["positions"]:
            return self.data["positions"][position_lower]
        
        # Tìm kiếm gần đúng
        for pos_key, pos_data in self.data["positions"].items():
            if position_lower in pos_key or pos_key in position_lower:
                return pos_data
            if position_lower in pos_data["name"].lower():
                return pos_data
        
        return None
    
    def generate_personalized_roadmap(self, position: str, experience_level: str = "fresher", 
                                    specific_interests: List[str] = None) -> str:
        """Tạo lộ trình cá nhân hóa dựa trên vị trí và yêu cầu cụ thể"""
        
        roadmap_data = self.get_roadmap_for_position(position)
        if not roadmap_data:
            return self.generate_custom_roadmap(position, experience_level, specific_interests)
        
        # Chuẩn bị context cho AI
        context = f"""
Vị trí: {roadmap_data['name']}
Kinh nghiệm: {experience_level}
Timeline: {roadmap_data['timeline']}

Tài liệu cần đọc:
{chr(10).join(['- ' + doc for doc in roadmap_data['documents']])}

Khóa học được đề xuất:
{chr(10).join(['- ' + course for course in roadmap_data['courses']])}

Milestones:
{chr(10).join(['- ' + milestone for milestone in roadmap_data['milestones']])}

Tài liệu chung cho tất cả nhân viên:
{chr(10).join(['- ' + doc for doc in self.data['general_onboarding']['documents']])}

Khóa học chung:
{chr(10).join(['- ' + course for course in self.data['general_onboarding']['courses']])}
"""
        
        if specific_interests:
            context += f"\n\nSở thích/Mối quan tâm đặc biệt: {', '.join(specific_interests)}"
        
        # Gọi AI để tạo lộ trình cá nhân hóa
        prompt = f"""
Dựa trên thông tin sau, hãy tạo một lộ trình onboarding cá nhân hóa chi tiết và thực tế:

{context}

Yêu cầu:
1. Sắp xếp lại thứ tự tài liệu và khóa học theo mức độ ưu tiên
2. Đưa ra timeline cụ thể cho từng item
3. Thêm các gợi ý thực tế để học hiệu quả
4. Tùy chỉnh dựa trên level kinh nghiệm
5. Bao gồm cả onboarding chung và chuyên môn
6. Đưa ra các checkpoint để đánh giá tiến độ

Trả lời bằng tiếng Việt, format rõ ràng và dễ đọc.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Lỗi khi tạo lộ trình: {e}"
    
    def generate_custom_roadmap(self, position: str, experience_level: str, 
                              specific_interests: List[str] = None) -> str:
        """Tạo lộ trình cho vị trí không có sẵn trong database"""
        
        interests_text = f"Sở thích: {', '.join(specific_interests)}" if specific_interests else ""
        
        prompt = f"""
Tạo một lộ trình onboarding chi tiết cho vị trí "{position}" với level kinh nghiệm "{experience_level}".
{interests_text}

Lộ trình cần bao gồm:
1. Tài liệu cần đọc (ưu tiên theo thứ tự)
2. Khóa học/training cần thiết
3. Timeline cụ thể (tuần/tháng)
4. Milestones và checkpoints
5. Các hoạt động thực hành
6. Onboarding chung của công ty

Onboarding chung bao gồm:
- Company handbook
- Organizational chart  
- IT security policies
- Benefits và compensation
- Company culture orientation
- IT security training
- Communication tools training
- Workplace safety

Trả lời bằng tiếng Việt, format rõ ràng và thực tế.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Lỗi khi tạo lộ trình tùy chỉnh: {e}"
    
    def add_position(self, position_key: str, position_data: Dict):
        """Thêm vị trí mới vào database"""
        self.data["positions"][position_key.lower()] = position_data
        self.save_data()
    
    def update_position(self, position_key: str, position_data: Dict):
        """Cập nhật thông tin vị trí"""
        if position_key.lower() in self.data["positions"]:
            self.data["positions"][position_key.lower()].update(position_data)
            self.save_data()
            return True
        return False
    
    def get_learning_suggestions(self, position: str, completed_items: List[str] = None) -> str:
        """Đưa ra gợi ý học tập tiếp theo dựa trên tiến độ hiện tại"""
        
        roadmap_data = self.get_roadmap_for_position(position)
        if not roadmap_data:
            return "Không tìm thấy thông tin cho vị trí này."
        
        completed_text = f"Đã hoàn thành: {', '.join(completed_items)}" if completed_items else "Chưa hoàn thành gì"
        
        prompt = f"""
Dựa trên lộ trình onboarding cho vị trí {roadmap_data['name']} và tiến độ hiện tại, hãy đưa ra gợi ý học tập tiếp theo:

Tài liệu có sẵn:
{chr(10).join(['- ' + doc for doc in roadmap_data['documents']])}

Khóa học có sẵn:
{chr(10).join(['- ' + course for course in roadmap_data['courses']])}

{completed_text}

Hãy đưa ra:
1. 3-5 item ưu tiên cao nhất để học tiếp theo
2. Lý do tại sao nên học những item này
3. Thời gian dự kiến cho mỗi item
4. Tips để học hiệu quả

Trả lời bằng tiếng Việt.
"""
        
        try:
            response = client.chat.completions.create(
                model="GPT-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Lỗi khi tạo gợi ý: {e}"

# Khởi tạo instance global
roadmap_manager = PersonalizedRoadmap()

