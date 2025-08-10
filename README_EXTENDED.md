# Chatbot Onboarding - Phiên Bản Mở Rộng

## Tổng Quan

Hệ thống Chatbot Onboarding đã được mở rộng với 3 chức năng chính mới:

1. **Tạo lộ trình onboarding cá nhân hóa** - Gợi ý tài liệu, khóa học phù hợp theo vị trí công việc
2. **Tạo nội dung tự động** - Soạn email chào mừng, tóm tắt tài liệu, sinh câu hỏi đào tạo
3. **Trích xuất thông tin tự động** - Tự điền biểu mẫu từ CV và giấy tờ của nhân viên mới

## Cấu Trúc Dự Án

```
OnboardingChatbot/
├── backend/
│   ├── chatbot.py              # Chatbot chính với tích hợp các chức năng mới
│   ├── server.py               # Flask API server với các endpoint mới
│   ├── personalized_roadmap.py # Module lộ trình cá nhân hóa
│   ├── content_generator.py    # Module tạo nội dung tự động
│   ├── document_extractor.py   # Module trích xuất thông tin
│   ├── embedding.py            # Xử lý embedding và QA
│   ├── chunking.py             # Xử lý tài liệu
│   ├── tts.py                  # Text-to-speech
│   ├── database/               # Cơ sở dữ liệu ChromaDB và JSON
│   ├── uploads/                # Thư mục upload file tạm thời
│   └── ...
├── frontend/                   # Giao diện người dùng
└── README_EXTENDED.md          # Tài liệu này
```

## Yêu Cầu Hệ Thống

### Python Dependencies

```bash
pip install openai chromadb flask flask-cors python-docx PyPDF2 pdfplumber pillow pytesseract
```

### Optional Dependencies (cho TTS)

```bash
pip install transformers torch soundfile
```

### System Dependencies

- Python 3.11+
- Tesseract OCR (cho xử lý ảnh)
- Git

## Cài Đặt và Chạy

### 1. Cài Đặt Dependencies

```bash
cd backend/
pip install -r requirements.txt
```

### 2. Cấu Hình API Keys

Cập nhật API keys trong các file:
- `chatbot.py`
- `personalized_roadmap.py` 
- `content_generator.py`
- `document_extractor.py`

### 3. Chạy Server

```bash
cd backend/
python server.py
```

Server sẽ chạy trên `http://localhost:5000`

## API Endpoints

### Chatbot Cơ Bản

#### POST /api/chatbot
Hỏi đáp với chatbot

**Request:**
```json
{
  "question": "Câu hỏi của bạn"
}
```

**Response:**
```json
{
  "response": "Câu trả lời từ chatbot"
}
```

### Lộ Trình Onboarding Cá Nhân Hóa

#### GET /api/roadmap/positions
Lấy danh sách các vị trí có sẵn

**Response:**
```json
{
  "positions": ["developer", "designer", "marketing", "hr", "sales"]
}
```

#### POST /api/roadmap/generate
Tạo lộ trình onboarding cá nhân hóa

**Request:**
```json
{
  "position": "developer",
  "experience_level": "fresher",
  "specific_interests": ["python", "web development"]
}
```

**Response:**
```json
{
  "roadmap": "Lộ trình chi tiết...",
  "position": "developer",
  "experience_level": "fresher"
}
```

#### POST /api/roadmap/suggestions
Lấy gợi ý học tập tiếp theo

**Request:**
```json
{
  "position": "developer",
  "completed_items": ["Git workflow", "Coding standards"]
}
```

#### GET /api/roadmap/position/{position_key}
Lấy chi tiết lộ trình cho vị trí cụ thể

### Tạo Nội Dung Tự Động

#### POST /api/content/welcome-email
Tạo email chào mừng

**Request:**
```json
{
  "employee_info": {
    "employee_name": "Nguyễn Văn A",
    "company_name": "ABC Corp",
    "position": "Developer",
    "start_date": "01/01/2024",
    "department": "IT",
    "manager_name": "Trần Thị B"
  }
}
```

#### POST /api/content/reminder-email
Tạo email nhắc nhở

**Request:**
```json
{
  "employee_name": "Nguyễn Văn A",
  "company_name": "ABC Corp",
  "pending_tasks": ["Hoàn thành training", "Nộp giấy tờ"],
  "deadline": "cuối tuần"
}
```

#### POST /api/content/summarize
Tóm tắt tài liệu

**Request:**
```json
{
  "document_text": "Nội dung tài liệu...",
  "summary_type": "general"
}
```

Các loại tóm tắt:
- `general`: Tóm tắt tổng quan
- `key_points`: Điểm chính
- `action_items`: Hành động cần thực hiện

#### POST /api/content/training-questions
Sinh câu hỏi đào tạo

**Request:**
```json
{
  "content": "Nội dung để tạo câu hỏi...",
  "question_type": "mixed",
  "num_questions": 5
}
```

Các loại câu hỏi:
- `mixed`: Hỗn hợp
- `multiple_choice`: Trắc nghiệm
- `true_false`: Đúng/Sai

#### POST /api/content/onboarding-checklist
Tạo checklist onboarding

**Request:**
```json
{
  "position": "developer",
  "department": "IT"
}
```

### Trích Xuất Thông Tin Tự Động

#### POST /api/extract/upload
Upload và xử lý tài liệu

**Request:** Form-data
- `file`: File tài liệu (PDF, DOCX, JPG, PNG)
- `document_type`: Loại tài liệu (`cv`, `id_card`, `diploma`, `general`)

#### POST /api/extract/text
Trích xuất thông tin từ text

**Request:**
```json
{
  "text": "Nội dung text...",
  "document_type": "cv"
}
```

#### POST /api/extract/auto-fill
Tự động điền biểu mẫu

**Request:**
```json
{
  "extracted_data": {...},
  "form_template": "employee_info_form"
}
```

#### GET /api/extract/form-templates
Lấy danh sách templates biểu mẫu

#### POST /api/extract/process-complete
Xử lý tài liệu hoàn chỉnh (upload -> extract -> auto-fill)

**Request:** Form-data
- `file`: File tài liệu
- `document_type`: Loại tài liệu
- `form_template`: Template biểu mẫu

## Sử Dụng Chatbot

### Lệnh Cơ Bản

- `help` hoặc `trợ giúp`: Hiển thị hướng dẫn
- Hỏi bất kỳ câu hỏi nào về onboarding

### Lệnh Lộ Trình Onboarding

- `Tạo lộ trình cho developer`
- `Gợi ý học tập cho marketing`
- `Lộ trình onboarding designer`

### Lệnh Tạo Nội Dung

- `Tạo email chào mừng`
- `Tóm tắt tài liệu`
- `Sinh câu hỏi đào tạo`

### Lệnh Trích Xuất Thông Tin

- `Xử lý CV`
- `Trích xuất thông tin từ giấy tờ`
- `Tự động điền biểu mẫu`

## Cấu Hình

### Thêm Vị Trí Mới

Chỉnh sửa file `backend/database/roadmap_data.json` để thêm vị trí mới:

```json
{
  "positions": {
    "new_position": {
      "name": "Tên vị trí",
      "documents": ["Tài liệu 1", "Tài liệu 2"],
      "courses": ["Khóa học 1", "Khóa học 2"],
      "timeline": "Thời gian",
      "milestones": ["Mốc 1", "Mốc 2"]
    }
  }
}
```

### Thêm Template Biểu Mẫu

Sử dụng API endpoint `/api/extract/form-templates` hoặc chỉnh sửa file `backend/database/form_templates.json`.

### Cấu Hình Email Templates

Chỉnh sửa file `backend/database/email_templates.json` để tùy chỉnh templates email.

## Troubleshooting

### Lỗi Import Module

Đảm bảo tất cả dependencies đã được cài đặt:
```bash
pip install -r requirements.txt
```

### Lỗi TTS

TTS sẽ tự động disable nếu không có transformers. Để enable:
```bash
pip install transformers torch soundfile
```

### Lỗi OCR

Cài đặt Tesseract:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-vie

# macOS
brew install tesseract tesseract-lang
```

### Lỗi ChromaDB

Xóa thư mục database và chạy lại embedding:
```bash
rm -rf backend/database/
python backend/embedding.py
```

## Triển Khai Production

### 1. Sử dụng WSGI Server

```bash
pip install gunicorn
cd backend/
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### 2. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Environment Variables

Thiết lập biến môi trường cho production:
```bash
export OPENAI_API_KEY="your-api-key"
export FLASK_ENV="production"
```

## Bảo Mật

- Không commit API keys vào git
- Sử dụng environment variables cho sensitive data
- Implement rate limiting cho API
- Validate và sanitize user input
- Sử dụng HTTPS trong production

## Monitoring và Logging

- Thêm logging cho các operations quan trọng
- Monitor API response times
- Track usage statistics
- Set up error alerting

## Phát Triển Tiếp

### Tính Năng Có Thể Thêm

1. **Authentication & Authorization**
   - User management
   - Role-based access control

2. **Advanced Analytics**
   - Onboarding progress tracking
   - Performance metrics
   - Usage analytics

3. **Integration**
   - HRMS integration
   - Calendar integration
   - Slack/Teams bot

4. **Mobile App**
   - React Native app
   - Push notifications

5. **Advanced AI Features**
   - Voice interaction
   - Multi-language support
   - Sentiment analysis

## Liên Hệ và Hỗ Trợ

Để được hỗ trợ hoặc báo cáo lỗi, vui lòng tạo issue trong repository hoặc liên hệ team phát triển.

