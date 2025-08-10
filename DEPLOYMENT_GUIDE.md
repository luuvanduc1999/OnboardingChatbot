# Hướng Dẫn Triển Khai Chatbot Onboarding

## Tổng Quan

Tài liệu này hướng dẫn chi tiết cách triển khai hệ thống Chatbot Onboarding từ môi trường development đến production.

## Chuẩn Bị Môi Trường

### Yêu Cầu Hệ Thống

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- OS: Ubuntu 20.04+ / CentOS 7+ / macOS 10.15+

**Recommended Requirements:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB
- OS: Ubuntu 22.04 LTS

### Software Dependencies

```bash
# Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Git
sudo apt install git

# Tesseract OCR (cho xử lý ảnh)
sudo apt install tesseract-ocr tesseract-ocr-vie

# Nginx (cho production)
sudo apt install nginx

# PM2 (cho process management)
npm install -g pm2
```

## Cài Đặt Ứng Dụng

### 1. Clone Repository

```bash
git clone <repository-url>
cd OnboardingChatbot
```

### 2. Tạo Virtual Environment

```bash
cd backend/
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài Đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Cấu Hình Environment Variables

Tạo file `.env`:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://aiportalapi.stu-platform.live/jpe
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_PATH=./database
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
```

### 5. Cập Nhật Cấu Hình

Chỉnh sửa các file cấu hình để sử dụng environment variables:

**server.py:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16*1024*1024))
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
```

### 6. Khởi Tạo Database

```bash
# Tạo thư mục database
mkdir -p database uploads

# Chạy embedding để tạo ChromaDB
python embedding.py
```

## Triển Khai Development

### Chạy Development Server

```bash
cd backend/
source venv/bin/activate
python server.py
```

Server sẽ chạy trên `http://localhost:5000`

### Test API Endpoints

```bash
# Test basic chatbot
curl -X POST http://localhost:5000/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"question": "help"}'

# Test roadmap
curl -X GET http://localhost:5000/api/roadmap/positions

# Test content generation
curl -X POST http://localhost:5000/api/content/welcome-email \
  -H "Content-Type: application/json" \
  -d '{"employee_info": {"employee_name": "Test User"}}'
```

## Triển Khai Production

### 1. Cấu Hình Gunicorn

Tạo file `gunicorn.conf.py`:

```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 2. Tạo Systemd Service

Tạo file `/etc/systemd/system/onboarding-chatbot.service`:

```ini
[Unit]
Description=Onboarding Chatbot API
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/OnboardingChatbot/backend
Environment=PATH=/path/to/OnboardingChatbot/backend/venv/bin
EnvironmentFile=/path/to/OnboardingChatbot/backend/.env
ExecStart=/path/to/OnboardingChatbot/backend/venv/bin/gunicorn -c gunicorn.conf.py server:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Khởi Động Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable onboarding-chatbot
sudo systemctl start onboarding-chatbot
sudo systemctl status onboarding-chatbot
```

### 4. Cấu Hình Nginx

Tạo file `/etc/nginx/sites-available/onboarding-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # File upload size limit
    client_max_body_size 16M;
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Static files (nếu có frontend)
    location / {
        root /path/to/OnboardingChatbot/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 5. Enable Nginx Site

```bash
sudo ln -s /etc/nginx/sites-available/onboarding-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring và Logging

### 1. Cấu Hình Logging

Thêm vào `server.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/onboarding-chatbot.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Onboarding Chatbot startup')
```

### 2. Health Check Endpoint

Thêm vào `server.py`:

```python
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
```

### 3. Monitoring với PM2 (Alternative)

```bash
# Cài đặt PM2
npm install -g pm2

# Tạo ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'onboarding-chatbot',
    script: 'venv/bin/gunicorn',
    args: '-c gunicorn.conf.py server:app',
    cwd: '/path/to/OnboardingChatbot/backend',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
EOF

# Khởi động
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Backup và Recovery

### 1. Backup Database

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/onboarding-chatbot"
SOURCE_DIR="/path/to/OnboardingChatbot/backend/database"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/database_$DATE.tar.gz -C $SOURCE_DIR .

# Giữ lại 7 backup gần nhất
find $BACKUP_DIR -name "database_*.tar.gz" -mtime +7 -delete
```

### 2. Cron Job cho Backup

```bash
# Thêm vào crontab
0 2 * * * /path/to/backup.sh
```

### 3. Recovery

```bash
# Restore database
cd /path/to/OnboardingChatbot/backend
tar -xzf /backups/onboarding-chatbot/database_YYYYMMDD_HHMMSS.tar.gz -C database/
sudo systemctl restart onboarding-chatbot
```

## Security

### 1. Firewall Configuration

```bash
# UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Hoặc iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 2. Rate Limiting

Thêm vào Nginx config:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        # ... rest of config
    }
}
```

### 3. API Key Security

```python
# Trong server.py
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/admin/endpoint')
@require_api_key
def admin_endpoint():
    # Protected endpoint
    pass
```

## Performance Optimization

### 1. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/roadmap/positions')
@cache.cached(timeout=300)  # Cache 5 minutes
def get_positions():
    # Cached response
    pass
```

### 2. Database Optimization

```python
# Connection pooling cho ChromaDB
import chromadb
from chromadb.config import Settings

chroma_client = chromadb.PersistentClient(
    path="./database",
    settings=Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./database"
    )
)
```

### 3. Async Processing

```python
from celery import Celery

celery = Celery('onboarding-chatbot')

@celery.task
def process_document_async(file_path, document_type):
    # Long-running task
    return document_extractor.process_document_file(file_path, document_type)
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   sudo chown -R ubuntu:ubuntu /path/to/OnboardingChatbot
   chmod +x /path/to/OnboardingChatbot/backend/server.py
   ```

3. **Module Not Found**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Database Connection Error**
   ```bash
   rm -rf database/
   python embedding.py
   ```

### Log Analysis

```bash
# Application logs
tail -f logs/onboarding-chatbot.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System logs
journalctl -u onboarding-chatbot -f
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **Clean Temporary Files**
   ```bash
   find uploads/ -type f -mtime +1 -delete
   ```

3. **Monitor Disk Space**
   ```bash
   df -h
   du -sh database/ logs/ uploads/
   ```

4. **Check Service Status**
   ```bash
   sudo systemctl status onboarding-chatbot
   sudo systemctl status nginx
   ```

### Update Deployment

```bash
# 1. Backup current version
cp -r /path/to/OnboardingChatbot /path/to/OnboardingChatbot.backup

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart service
sudo systemctl restart onboarding-chatbot

# 5. Verify deployment
curl http://localhost/health
```

## Scaling

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream chatbot_backend {
       server 127.0.0.1:5000;
       server 127.0.0.1:5001;
       server 127.0.0.1:5002;
   }
   
   server {
       location /api/ {
           proxy_pass http://chatbot_backend;
       }
   }
   ```

2. **Multiple Instances**
   ```bash
   # Instance 1
   gunicorn -c gunicorn.conf.py -b 127.0.0.1:5000 server:app
   
   # Instance 2
   gunicorn -c gunicorn.conf.py -b 127.0.0.1:5001 server:app
   ```

### Vertical Scaling

1. **Increase Workers**
   ```python
   # gunicorn.conf.py
   workers = multiprocessing.cpu_count() * 2 + 1
   ```

2. **Memory Optimization**
   ```python
   # Trong server.py
   import gc
   
   @app.after_request
   def after_request(response):
       gc.collect()
       return response
   ```

## Liên Hệ

Để được hỗ trợ triển khai, vui lòng liên hệ team phát triển hoặc tạo issue trong repository.

