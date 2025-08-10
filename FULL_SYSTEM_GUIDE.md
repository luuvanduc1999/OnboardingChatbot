# Hướng Dẫn Toàn Bộ Hệ Thống - Chatbot Onboarding

## Tổng Quan Hệ Thống

Hệ thống Chatbot Onboarding là một giải pháp AI toàn diện hỗ trợ quá trình onboarding nhân viên mới, bao gồm:

### 🎯 **Chức Năng Chính**
1. **Chatbot AI Hỗ Trợ:** Trả lời câu hỏi về chính sách, quy trình, phúc lợi
2. **Lộ Trình Cá Nhân Hóa:** Tạo lộ trình onboarding theo vị trí công việc
3. **Tạo Nội Dung Tự Động:** Email chào mừng, tóm tắt tài liệu, câu hỏi đào tạo
4. **Trích Xuất Thông Tin:** Xử lý CV, CMND/CCCD và tự động điền biểu mẫu

### 🏗️ **Kiến Trúc Hệ Thống**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │◄──►│   (Flask)       │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • UI Components │    │ • API Endpoints │    │ • OpenAI API    │
│ • State Mgmt    │    │ • Business Logic│    │ • ChromaDB      │
│ • API Calls     │    │ • Data Processing│   │ • File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Cài Đặt và Triển Khai

### 📋 **Yêu Cầu Hệ Thống**

- **Python:** 3.11+
- **Node.js:** 20.18.0+
- **Package Managers:** pip3, pnpm
- **RAM:** Tối thiểu 4GB (khuyến nghị 8GB+)
- **Disk:** Tối thiểu 2GB free space

### 🚀 **Cài Đặt Nhanh**

#### 1. Clone và Setup Project

```bash
# Giải nén project (nếu có file zip)
unzip OnboardingChatbot_Extended.tar.gz
cd OnboardingChatbot/OnboardingChatbot/
```

#### 2. Setup Backend

```bash
cd backend/
pip3 install -r requirements.txt

# Cấu hình OpenAI API Key (tùy chọn)
export OPENAI_API_KEY="your-api-key-here"

# Khởi động server
python3.11 server.py
```

Backend sẽ chạy trên `http://localhost:5000`

#### 3. Setup Frontend

```bash
cd ../frontend/
pnpm install

# Khởi động development server
pnpm run dev --host
```

Frontend sẽ chạy trên `http://localhost:5173`

### 🔧 **Cấu Hình Chi Tiết**

#### Backend Configuration

**File:** `backend/server.py`
```python
# Server settings
app.run(host='0.0.0.0', port=5000, debug=True)

# CORS settings
CORS(app)
```

**OpenAI API Keys:** Cập nhật trong các file:
- `chatbot.py`
- `personalized_roadmap.py`
- `content_generator.py`
- `document_extractor.py`

#### Frontend Configuration

**File:** `frontend/src/components/*.jsx`
```javascript
// API Base URL
const API_BASE = 'http://localhost:5000'
```

## Sử Dụng Hệ Thống

### 🤖 **1. Chatbot AI**

**Truy cập:** Tab "Chatbot" trên giao diện chính

**Cách sử dụng:**
```
Người dùng: "Chính sách nghỉ phép như thế nào?"
Chatbot: "Theo chính sách công ty, nhân viên được nghỉ phép..."

Người dùng: "help"
Chatbot: [Hiển thị hướng dẫn đầy đủ]
```

**Lệnh đặc biệt:**
- `help` - Xem hướng dẫn
- `Tạo lộ trình cho [vị trí]` - Chuyển đến tạo lộ trình
- `Tạo email chào mừng` - Chuyển đến tạo nội dung
- `Xử lý CV` - Chuyển đến trích xuất tài liệu

### 🎯 **2. Lộ Trình Onboarding Cá Nhân Hóa**

**Truy cập:** Tab "Lộ trình"

**Quy trình:**
1. Chọn vị trí công việc (Developer, Designer, Marketing, HR, Sales)
2. Chọn mức độ kinh nghiệm (Fresher, Junior, Senior)
3. Click "Tạo Lộ Trình"
4. Xem lộ trình chi tiết với timeline và nhiệm vụ cụ thể

**Kết quả bao gồm:**
- Lộ trình theo thời gian (Ngày 1, Tuần 1, Tháng 1)
- Nhiệm vụ cụ thể cho từng giai đoạn
- Tài liệu và khóa học gợi ý
- Mục tiêu và milestone

### 📝 **3. Tạo Nội Dung Tự Động**

**Truy cập:** Tab "Nội dung"

#### 3.1 Email Chào Mừng
```
Input:
- Tên nhân viên: Nguyễn Văn An
- Công ty: TechViet Solutions
- Vị trí: Senior Developer
- Ngày bắt đầu: 15/01/2024
- Phòng ban: IT
- Quản lý: Trần Thị Bình

Output:
- Subject: Email chào mừng chuyên nghiệp
- Body: Nội dung email đầy đủ với thông tin cá nhân hóa
```

#### 3.2 Tóm Tắt Tài Liệu
```
Input:
- Nội dung tài liệu (text)
- Loại tóm tắt: Tổng quan/Điểm chính/Hành động

Output:
- Tóm tắt ngắn gọn, súc tích
- Phù hợp với loại tóm tắt đã chọn
```

#### 3.3 Câu Hỏi Đào Tạo
```
Input:
- Nội dung học liệu
- Loại câu hỏi: Trắc nghiệm/Đúng-Sai/Hỗn hợp
- Số lượng câu hỏi: 1-20

Output:
- Danh sách câu hỏi với đáp án
- Giải thích cho từng câu hỏi
- Format phù hợp cho đào tạo
```

#### 3.4 Checklist Onboarding
```
Input:
- Vị trí công việc
- Phòng ban

Output:
- Checklist theo timeline (Ngày 1, Tuần 1, Tháng 1)
- Nhiệm vụ cụ thể với người chịu trách nhiệm
- Thời gian ước tính và độ ưu tiên
```

### 📄 **4. Trích Xuất Thông Tin Tự Động**

**Truy cập:** Tab "Tài liệu"

**Quy trình:**
1. **Upload:** Kéo thả hoặc chọn file (PDF, DOCX, DOC, TXT, JPG, PNG)
2. **Trích xuất:** Hệ thống tự động phân tích và trích xuất thông tin
3. **Biểu mẫu:** Xem và chỉnh sửa thông tin đã được tự động điền

**Loại tài liệu hỗ trợ:**
- **CV/Resume:** Tên, email, phone, địa chỉ, học vấn, kinh nghiệm, kỹ năng
- **CMND/CCCD:** Số ID, tên, ngày sinh, địa chỉ
- **Bằng cấp:** Trường học, chuyên ngành, năm tốt nghiệp
- **Tài liệu khác:** Thông tin tùy theo nội dung

## API Documentation

### 🔌 **Backend API Endpoints**

#### Chatbot APIs
```
POST /api/chatbot
Body: {"question": "string"}
Response: {"response": "string"}
```

#### Roadmap APIs
```
GET /api/roadmap/positions
Response: {"positions": ["developer", "designer", ...]}

POST /api/roadmap/generate
Body: {"position": "string", "experience_level": "string"}
Response: {"roadmap": "string"}
```

#### Content Generation APIs
```
POST /api/content/welcome-email
Body: {"employee_info": {...}}
Response: {"email": {"subject": "string", "body": "string"}}

POST /api/content/summarize
Body: {"document_text": "string", "summary_type": "string"}
Response: {"summary": "string"}

POST /api/content/training-questions
Body: {"content": "string", "question_type": "string", "num_questions": int}
Response: {"questions": [...]}

POST /api/content/onboarding-checklist
Body: {"position": "string", "department": "string"}
Response: {"checklist": [...]}
```

#### Document Extraction APIs
```
POST /api/extract/document
Body: FormData with file
Response: {"extracted_info": {...}}

POST /api/extract/auto-fill
Body: {"extracted_info": {...}}
Response: {"form_data": {...}}
```

## Triển Khai Production

### 🌐 **Deployment Options**

#### Option 1: Manual Deployment

**Backend:**
```bash
# Install production dependencies
pip3 install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

**Frontend:**
```bash
# Build for production
pnpm run build

# Serve with nginx or apache
cp -r dist/* /var/www/html/
```

#### Option 2: Docker Deployment

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN pnpm install
COPY . .
RUN pnpm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

#### Option 3: Cloud Deployment

**Heroku, AWS, Google Cloud, Azure** - Sử dụng các service tương ứng với cấu hình container hoặc serverless.

### 🔒 **Security Considerations**

1. **API Keys:** Sử dụng environment variables
2. **CORS:** Cấu hình chỉ cho phép domain cụ thể
3. **File Upload:** Validate file types và size
4. **Rate Limiting:** Implement để tránh abuse
5. **HTTPS:** Bắt buộc trong production

## Monitoring và Maintenance

### 📊 **Logging**

Backend tự động log các hoạt động:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 🔍 **Health Checks**

```bash
# Backend health
curl http://localhost:5000/api/roadmap/positions

# Frontend health
curl http://localhost:5173
```

### 🔄 **Updates và Backup**

1. **Code Updates:** Git pull và restart services
2. **Dependencies:** Định kỳ update packages
3. **Data Backup:** Backup ChromaDB và uploaded files
4. **Logs:** Rotate và archive logs định kỳ

## Troubleshooting

### ❗ **Lỗi Thường Gặp**

#### Backend Issues
```bash
# Port already in use
sudo lsof -t -i:5000
sudo kill -9 <PID>

# Missing dependencies
pip3 install -r requirements.txt

# OpenAI API errors
export OPENAI_API_KEY="your-key"
```

#### Frontend Issues
```bash
# Node modules issues
rm -rf node_modules package-lock.json
pnpm install

# Build errors
pnpm run build --verbose

# CORS errors
# Check backend CORS configuration
```

#### Integration Issues
```bash
# API connection failed
# Check both servers are running
# Verify API URLs in frontend code
# Check network/firewall settings
```

### 🆘 **Support và Debugging**

1. **Logs:** Kiểm tra console logs (F12 trong browser)
2. **Network:** Kiểm tra API calls trong Network tab
3. **Server Logs:** Kiểm tra terminal output của backend
4. **File Permissions:** Đảm bảo quyền đọc/ghi files

## Kết Luận

Hệ thống Chatbot Onboarding cung cấp giải pháp AI toàn diện cho quá trình onboarding nhân viên mới. Với kiến trúc modular và giao diện thân thiện, hệ thống có thể dễ dàng tùy chỉnh và mở rộng theo nhu cầu cụ thể của từng tổ chức.

### 🎉 **Lợi Ích Chính**

- **Tự động hóa:** Giảm 80% thời gian xử lý thủ công
- **Cá nhân hóa:** Lộ trình phù hợp với từng vị trí
- **Thông minh:** AI hỗ trợ 24/7
- **Hiệu quả:** Xử lý đồng thời nhiều nhân viên mới
- **Mở rộng:** Dễ dàng thêm chức năng mới

### 📞 **Liên Hệ Hỗ Trợ**

Để được hỗ trợ kỹ thuật hoặc tùy chỉnh thêm tính năng, vui lòng liên hệ team phát triển với thông tin chi tiết về vấn đề gặp phải.

