# Hướng Dẫn Sử Dụng Frontend - Chatbot Onboarding

## Tổng Quan

Giao diện người dùng (Frontend) của hệ thống Chatbot Onboarding được xây dựng bằng React với Tailwind CSS và shadcn/ui components, cung cấp trải nghiệm người dùng hiện đại và thân thiện.

## Cấu Trúc Dự Án

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── ChatbotInterface.jsx
│   │   ├── RoadmapGenerator.jsx
│   │   ├── ContentGenerator.jsx
│   │   └── DocumentExtractor.jsx
│   ├── App.jsx           # Main application component
│   ├── App.css           # Global styles
│   └── main.jsx          # Entry point
├── package.json          # Dependencies and scripts
└── vite.config.js        # Vite configuration
```

## Cài Đặt và Chạy

### 1. Cài Đặt Dependencies

```bash
cd frontend/
pnpm install
```

### 2. Khởi Động Development Server

```bash
pnpm run dev --host
```

Server sẽ chạy trên `http://localhost:5173` (hoặc port khác nếu 5173 đã được sử dụng).

### 3. Build cho Production

```bash
pnpm run build
```

## Các Chức Năng Chính

### 1. Chatbot AI (ChatbotInterface.jsx)

**Mô tả:** Giao diện chat tương tác với AI chatbot

**Tính năng:**
- Chat real-time với backend API
- Gợi ý câu hỏi thông dụng
- Hiển thị lịch sử chat
- Loading states và error handling

**API Endpoint:** `POST /api/chatbot`

**Cách sử dụng:**
1. Nhập câu hỏi vào ô input
2. Click nút Send hoặc nhấn Enter
3. Xem phản hồi từ chatbot
4. Sử dụng các gợi ý câu hỏi để test nhanh

### 2. Tạo Lộ Trình Onboarding (RoadmapGenerator.jsx)

**Mô tả:** Tạo lộ trình onboarding cá nhân hóa theo vị trí công việc

**Tính năng:**
- Chọn vị trí công việc từ dropdown
- Chọn mức độ kinh nghiệm
- Tạo lộ trình chi tiết
- Hiển thị kết quả với format đẹp

**API Endpoints:**
- `GET /api/roadmap/positions` - Lấy danh sách vị trí
- `POST /api/roadmap/generate` - Tạo lộ trình

**Cách sử dụng:**
1. Chọn vị trí công việc (Developer, Designer, Marketing, HR, Sales)
2. Chọn mức độ kinh nghiệm (Fresher, Junior, Senior)
3. Click "Tạo Lộ Trình"
4. Xem lộ trình chi tiết được tạo

### 3. Tạo Nội Dung Tự Động (ContentGenerator.jsx)

**Mô tả:** Tự động tạo các loại nội dung khác nhau

**Tính năng:**
- **Email chào mừng:** Tạo email cho nhân viên mới
- **Tóm tắt tài liệu:** Tóm tắt theo nhiều kiểu
- **Câu hỏi đào tạo:** Tạo câu hỏi trắc nghiệm
- **Checklist onboarding:** Tạo checklist theo vị trí

**API Endpoints:**
- `POST /api/content/welcome-email`
- `POST /api/content/summarize`
- `POST /api/content/training-questions`
- `POST /api/content/onboarding-checklist`

**Cách sử dụng:**
1. Chọn tab tương ứng (Email, Tóm tắt, Câu hỏi, Checklist)
2. Điền thông tin cần thiết
3. Click nút tạo tương ứng
4. Copy hoặc download kết quả

### 4. Trích Xuất Thông Tin (DocumentExtractor.jsx)

**Mô tả:** Upload và trích xuất thông tin từ tài liệu

**Tính năng:**
- Upload file drag & drop
- Hỗ trợ PDF, DOCX, DOC, TXT, JPG, PNG
- Trích xuất thông tin tự động
- Tự động điền biểu mẫu

**API Endpoints:**
- `POST /api/extract/document`
- `POST /api/extract/auto-fill`

**Cách sử dụng:**
1. Tab Upload: Kéo thả file hoặc click để chọn
2. Tab Trích xuất: Xem thông tin đã trích xuất
3. Tab Biểu mẫu: Xem và chỉnh sửa thông tin tự động điền

## Cấu Hình API

Frontend kết nối với backend qua các API calls. Đảm bảo backend server đang chạy trên `http://localhost:5000`.

### Xử Lý CORS

Backend đã được cấu hình CORS để cho phép frontend truy cập:

```python
from flask_cors import CORS
CORS(app)
```

### Error Handling

Tất cả các API calls đều có error handling:

```javascript
try {
  const response = await fetch(url, options)
  if (!response.ok) throw new Error('Network response was not ok')
  const data = await response.json()
  // Handle success
} catch (error) {
  console.error('Error:', error)
  // Handle error
}
```

## Styling và UI

### Tailwind CSS

Sử dụng Tailwind CSS cho styling với các utility classes:

```jsx
<div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
  <h3 className="text-lg font-semibold text-blue-800">Title</h3>
</div>
```

### shadcn/ui Components

Sử dụng các component từ shadcn/ui:

```jsx
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
```

### Responsive Design

Giao diện được thiết kế responsive:

```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

## Deployment

### Development

```bash
pnpm run dev --host
```

### Production Build

```bash
pnpm run build
pnpm run preview
```

### Deploy với Nginx

1. Build project: `pnpm run build`
2. Copy thư mục `dist/` đến web server
3. Cấu hình Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Lỗi Thường Gặp

1. **CORS Error:**
   - Đảm bảo backend có CORS enabled
   - Kiểm tra URL API đúng

2. **API Connection Failed:**
   - Kiểm tra backend server đang chạy
   - Kiểm tra port và URL

3. **Component Not Rendering:**
   - Kiểm tra import paths
   - Kiểm tra console errors

### Debug Tips

1. Mở Developer Tools (F12)
2. Kiểm tra Console tab cho errors
3. Kiểm tra Network tab cho API calls
4. Sử dụng React Developer Tools extension

## Tính Năng Nâng Cao

### State Management

Sử dụng React hooks cho state management:

```jsx
const [data, setData] = useState(null)
const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)
```

### Loading States

Hiển thị loading indicators:

```jsx
{isLoading ? (
  <Loader2 className="h-4 w-4 animate-spin" />
) : (
  <Send className="h-4 w-4" />
)}
```

### Error Boundaries

Xử lý errors gracefully trong components.

## Kết Luận

Frontend cung cấp giao diện hoàn chỉnh cho tất cả các chức năng của hệ thống Chatbot Onboarding. Với thiết kế hiện đại và trải nghiệm người dùng tốt, người dùng có thể dễ dàng tương tác với các tính năng AI một cách trực quan và hiệu quả.

