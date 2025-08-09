# API Documentation - Chatbot Onboarding

## Tổng Quan

API này cung cấp các endpoint để tương tác với hệ thống Chatbot Onboarding, bao gồm các chức năng:
- Chatbot hỏi đáp cơ bản
- Tạo lộ trình onboarding cá nhân hóa
- Tạo nội dung tự động
- Trích xuất thông tin từ tài liệu

**Base URL:** `http://localhost:5000/api`

**Content-Type:** `application/json` (trừ khi có ghi chú khác)

## Authentication

Hiện tại API không yêu cầu authentication. Trong production, nên implement API key hoặc JWT token.

## Error Handling

Tất cả API endpoints trả về error theo format:

```json
{
  "error": "Mô tả lỗi",
  "details": "Chi tiết lỗi (optional)"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Chatbot API

### POST /api/chatbot

Gửi câu hỏi đến chatbot và nhận câu trả lời.

**Request:**
```json
{
  "question": "string"
}
```

**Response:**
```json
{
  "response": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"question": "Chính sách nghỉ phép của công ty như thế nào?"}'
```

**Response:**
```json
{
  "response": "Theo chính sách của công ty, nhân viên được nghỉ phép 12 ngày/năm..."
}
```

### POST /api/tts

Chuyển đổi text thành speech.

**Request:**
```json
{
  "text": "string"
}
```

**Response:** Audio file (WAV format)

## Lộ Trình Onboarding API

### GET /api/roadmap/positions

Lấy danh sách các vị trí có sẵn.

**Response:**
```json
{
  "positions": ["string"]
}
```

**Example:**
```bash
curl -X GET http://localhost:5000/api/roadmap/positions
```

**Response:**
```json
{
  "positions": ["developer", "designer", "marketing", "hr", "sales"]
}
```

### POST /api/roadmap/generate

Tạo lộ trình onboarding cá nhân hóa.

**Request:**
```json
{
  "position": "string",
  "experience_level": "string",
  "specific_interests": ["string"]
}
```

**Parameters:**
- `position`: Vị trí công việc (required)
- `experience_level`: Mức độ kinh nghiệm (optional, default: "fresher")
- `specific_interests`: Sở thích cụ thể (optional)

**Response:**
```json
{
  "roadmap": "string",
  "position": "string",
  "experience_level": "string",
  "generated_at": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/roadmap/generate \
  -H "Content-Type: application/json" \
  -d '{
    "position": "developer",
    "experience_level": "fresher",
    "specific_interests": ["python", "web development"]
  }'
```

### POST /api/roadmap/suggestions

Lấy gợi ý học tập tiếp theo dựa trên tiến độ hiện tại.

**Request:**
```json
{
  "position": "string",
  "completed_items": ["string"]
}
```

**Response:**
```json
{
  "suggestions": ["string"],
  "next_milestones": ["string"],
  "estimated_time": "string"
}
```

### GET /api/roadmap/position/{position_key}

Lấy chi tiết lộ trình cho vị trí cụ thể.

**Parameters:**
- `position_key`: Key của vị trí (developer, designer, marketing, hr, sales)

**Response:**
```json
{
  "position": "string",
  "documents": ["string"],
  "courses": ["string"],
  "timeline": "string",
  "milestones": ["string"]
}
```

## Content Generation API

### POST /api/content/welcome-email

Tạo email chào mừng cho nhân viên mới.

**Request:**
```json
{
  "employee_info": {
    "employee_name": "string",
    "company_name": "string",
    "position": "string",
    "start_date": "string",
    "department": "string",
    "manager_name": "string"
  }
}
```

**Response:**
```json
{
  "email": {
    "subject": "string",
    "body": "string",
    "sender": "string"
  },
  "generated_at": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/content/welcome-email \
  -H "Content-Type: application/json" \
  -d '{
    "employee_info": {
      "employee_name": "Nguyễn Văn A",
      "company_name": "ABC Corp",
      "position": "Developer",
      "start_date": "01/01/2024",
      "department": "IT",
      "manager_name": "Trần Thị B"
    }
  }'
```

### POST /api/content/reminder-email

Tạo email nhắc nhở cho nhân viên.

**Request:**
```json
{
  "employee_name": "string",
  "company_name": "string",
  "pending_tasks": ["string"],
  "deadline": "string"
}
```

**Response:**
```json
{
  "email": {
    "subject": "string",
    "body": "string"
  },
  "generated_at": "string"
}
```

### POST /api/content/summarize

Tóm tắt tài liệu.

**Request:**
```json
{
  "document_text": "string",
  "summary_type": "string"
}
```

**Parameters:**
- `summary_type`: Loại tóm tắt
  - `general`: Tóm tắt tổng quan
  - `key_points`: Điểm chính
  - `action_items`: Hành động cần thực hiện

**Response:**
```json
{
  "summary": "string",
  "summary_type": "string",
  "original_length": "number",
  "generated_at": "string"
}
```

### POST /api/content/training-questions

Sinh câu hỏi đào tạo từ nội dung.

**Request:**
```json
{
  "content": "string",
  "question_type": "string",
  "num_questions": "number"
}
```

**Parameters:**
- `question_type`: Loại câu hỏi
  - `mixed`: Hỗn hợp
  - `multiple_choice`: Trắc nghiệm
  - `true_false`: Đúng/Sai
- `num_questions`: Số lượng câu hỏi (default: 5)

**Response:**
```json
{
  "questions": [
    {
      "question": "string",
      "type": "string",
      "options": ["string"],
      "correct_answer": "string",
      "explanation": "string"
    }
  ],
  "question_type": "string",
  "num_questions": "number",
  "generated_at": "string"
}
```

### POST /api/content/onboarding-checklist

Tạo checklist onboarding cho vị trí cụ thể.

**Request:**
```json
{
  "position": "string",
  "department": "string"
}
```

**Response:**
```json
{
  "checklist": {
    "pre_start": ["string"],
    "first_day": ["string"],
    "first_week": ["string"],
    "first_month": ["string"]
  },
  "position": "string",
  "department": "string",
  "generated_at": "string"
}
```

## Document Extraction API

### POST /api/extract/upload

Upload và xử lý tài liệu.

**Request:** `multipart/form-data`
- `file`: File tài liệu (PDF, DOCX, DOC, TXT, JPG, JPEG, PNG)
- `document_type`: Loại tài liệu (cv, id_card, diploma, general)

**Response:**
```json
{
  "result": {
    "file_path": "string",
    "document_type": "string",
    "extracted_text": "string",
    "extracted_data": "object",
    "processing_status": "string"
  },
  "processed_at": "string"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/extract/upload \
  -F "file=@cv.pdf" \
  -F "document_type=cv"
```

### POST /api/extract/text

Trích xuất thông tin từ text có sẵn.

**Request:**
```json
{
  "text": "string",
  "document_type": "string"
}
```

**Response:**
```json
{
  "extracted_data": "object",
  "document_type": "string",
  "processed_at": "string"
}
```

### POST /api/extract/auto-fill

Tự động điền biểu mẫu từ dữ liệu đã trích xuất.

**Request:**
```json
{
  "extracted_data": "object",
  "form_template": "string"
}
```

**Parameters:**
- `form_template`: Template biểu mẫu
  - `employee_info_form`: Thông tin nhân viên
  - `contract_form`: Thông tin hợp đồng

**Response:**
```json
{
  "filled_form": {
    "form_name": "string",
    "fields": "object",
    "missing_fields": ["string"],
    "confidence": "object"
  },
  "form_template": "string",
  "processed_at": "string"
}
```

### GET /api/extract/form-templates

Lấy danh sách templates biểu mẫu có sẵn.

**Response:**
```json
{
  "templates": {
    "template_name": {
      "name": "string",
      "fields": [
        {
          "field": "string",
          "label": "string",
          "type": "string",
          "required": "boolean"
        }
      ]
    }
  }
}
```

### POST /api/extract/form-templates

Thêm template biểu mẫu mới.

**Request:**
```json
{
  "template_name": "string",
  "template_data": {
    "name": "string",
    "fields": [
      {
        "field": "string",
        "label": "string",
        "type": "string",
        "required": "boolean"
      }
    ]
  }
}
```

**Response:**
```json
{
  "message": "Template added successfully",
  "template_name": "string"
}
```

### POST /api/extract/process-complete

Xử lý tài liệu hoàn chỉnh: upload → extract → auto-fill.

**Request:** `multipart/form-data`
- `file`: File tài liệu
- `document_type`: Loại tài liệu
- `form_template`: Template biểu mẫu

**Response:**
```json
{
  "document_processing": "object",
  "auto_filled_form": "object",
  "processed_at": "string"
}
```

## Data Models

### Employee Info

```json
{
  "employee_name": "string",
  "company_name": "string",
  "position": "string",
  "start_date": "string",
  "department": "string",
  "manager_name": "string",
  "email": "string",
  "phone": "string"
}
```

### CV Data

```json
{
  "personal_info": {
    "full_name": "string",
    "email": "string",
    "phone": "string",
    "address": "string",
    "birth_date": "string"
  },
  "education": [
    {
      "school": "string",
      "major": "string",
      "degree": "string",
      "graduation_year": "string"
    }
  ],
  "experience": [
    {
      "company": "string",
      "position": "string",
      "duration": "string",
      "description": "string"
    }
  ],
  "skills": {
    "technical": ["string"],
    "soft_skills": ["string"],
    "languages": ["string"]
  },
  "certifications": [
    {
      "name": "string",
      "issuer": "string",
      "year": "string"
    }
  ],
  "projects": [
    {
      "name": "string",
      "role": "string",
      "technologies": ["string"],
      "description": "string"
    }
  ],
  "interests": ["string"]
}
```

### Training Question

```json
{
  "question": "string",
  "type": "multiple_choice|true_false|open_ended",
  "options": ["string"],
  "correct_answer": "string",
  "explanation": "string"
}
```

## Rate Limiting

Hiện tại không có rate limiting. Trong production nên implement:
- 100 requests/minute cho user thông thường
- 1000 requests/minute cho admin
- 10 requests/minute cho file upload

## File Upload Limits

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, DOC, TXT, JPG, JPEG, PNG
- Files are automatically deleted after processing

## Webhooks (Future Feature)

Có thể implement webhooks để notify khi:
- Document processing completed
- Onboarding milestone reached
- Training questions answered

## SDK và Libraries

### Python SDK Example

```python
import requests

class OnboardingChatbotAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def ask_chatbot(self, question):
        response = requests.post(
            f"{self.base_url}/chatbot",
            json={"question": question}
        )
        return response.json()
    
    def generate_roadmap(self, position, experience_level="fresher"):
        response = requests.post(
            f"{self.base_url}/roadmap/generate",
            json={
                "position": position,
                "experience_level": experience_level
            }
        )
        return response.json()
    
    def upload_document(self, file_path, document_type="cv"):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/extract/upload",
                files={"file": f},
                data={"document_type": document_type}
            )
        return response.json()

# Usage
api = OnboardingChatbotAPI()
result = api.ask_chatbot("Chính sách nghỉ phép như thế nào?")
print(result["response"])
```

### JavaScript SDK Example

```javascript
class OnboardingChatbotAPI {
    constructor(baseUrl = "http://localhost:5000/api") {
        this.baseUrl = baseUrl;
    }
    
    async askChatbot(question) {
        const response = await fetch(`${this.baseUrl}/chatbot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        return response.json();
    }
    
    async generateRoadmap(position, experienceLevel = "fresher") {
        const response = await fetch(`${this.baseUrl}/roadmap/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                position,
                experience_level: experienceLevel
            })
        });
        return response.json();
    }
    
    async uploadDocument(file, documentType = "cv") {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', documentType);
        
        const response = await fetch(`${this.baseUrl}/extract/upload`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }
}

// Usage
const api = new OnboardingChatbotAPI();
api.askChatbot("Chính sách nghỉ phép như thế nào?")
   .then(result => console.log(result.response));
```

## Testing

### Unit Tests

```bash
# Chạy tests
python -m pytest tests/

# Test coverage
python -m pytest --cov=. tests/
```

### Integration Tests

```bash
# Test API endpoints
python tests/test_api.py

# Test với sample data
python tests/test_integration.py
```

### Load Testing

```bash
# Sử dụng Apache Bench
ab -n 1000 -c 10 http://localhost:5000/api/chatbot

# Sử dụng wrk
wrk -t12 -c400 -d30s http://localhost:5000/api/chatbot
```

## Changelog

### Version 1.0.0
- Initial release với 3 chức năng chính
- Basic chatbot functionality
- Personalized roadmap generation
- Content generation
- Document extraction

### Future Versions
- Authentication & authorization
- Advanced analytics
- Multi-language support
- Voice interaction
- Mobile app integration

## Support

Để được hỗ trợ API:
1. Kiểm tra documentation này
2. Xem examples trong repository
3. Tạo issue trên GitHub
4. Liên hệ team phát triển

