# Deployment Guide

## Development vs Production

### Development Setup (Local)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Quick Start

```bash
# From project root
docker-compose up --build

# Access at http://localhost:3000
```

### Production Docker

```bash
# Build images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Run containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f
```

---

## Cloud Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend - Vercel

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. From frontend directory
cd frontend
vercel

# 3. Follow prompts to connect GitHub
# 4. Set environment variables in Vercel dashboard:
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

#### Backend - Railway

```bash
# 1. Connect Railway to GitHub
# 2. Create new project from repository
# 3. Configure service:
#    - Root: ./backend
#    - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
# 4. Add environment variables:
#    - GROQ_API_KEY=your_key
#    - PORT=8000

# 5. Deploy (automatic on push)
```

### Option 2: Heroku (Legacy)

```bash
# Install Heroku CLI
# Login: heroku login

# Backend deployment
cd backend
heroku create your-app-backend
heroku config:set GROQ_API_KEY=your_key
git push heroku main

# Frontend deployment
cd ../frontend
vercel --prod
```

### Option 3: AWS (EC2 + S3)

#### Backend (EC2)

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Connect via SSH

# 3. Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3-pip python3.11-venv

# 4. Deploy code
git clone your-repo
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Setup systemd service
sudo nano /etc/systemd/system/copilot-backend.service
```

**Service file:**
```ini
[Unit]
Description=Healthcare Pre-Auth Copilot Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
Environment="PATH=/home/ubuntu/backend/venv/bin"
Environment="GROQ_API_KEY=your_key"
ExecStart=/home/ubuntu/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 6. Enable and start
sudo systemctl enable copilot-backend
sudo systemctl start copilot-backend
```

#### Frontend (S3 + CloudFront)

```bash
# 1. Build Next.js
cd frontend
npm run build

# 2. Deploy static files to S3
aws s3 sync .next/static s3://your-bucket/

# 3. Create CloudFront distribution
# 4. Set environment variable to CloudFront URL
```

### Option 4: Google Cloud (App Engine)

#### Backend - Cloud Run

```yaml
# app.yaml
runtime: python311

env: standard

entrypoint: uvicorn app.main:app --host 0.0.0.0 --port 8080

env_variables:
  GROQ_API_KEY: your_key
```

```bash
gcloud app deploy
```

#### Frontend - Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
npm run build
firebase deploy
```

---

## Environment Configuration

### Production Environment Variables

#### Backend (.env)

```bash
# API Configuration
GROQ_API_KEY=your_production_key
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Security (recommended)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
MAX_FILE_SIZE=10485760  # 10MB
LOG_LEVEL=INFO

# Database (if added)
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
```

#### Frontend (.env.production)

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## Performance Optimization

### Backend

```python
# 1. Use production ASGI server
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# 2. Enable compression
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 3. Add caching headers
@app.get("/health", headers={"cache-control": "max-age=60"})

# 4. Rate limiting
pip install slowapi
from slowapi import Limiter
```

### Frontend

```bash
# 1. Build optimization
npm run build

# 2. Image optimization (Next.js built-in)
# 3. Code splitting (dynamic imports)
# 4. CSS optimization (Tailwind)
```

---

## Monitoring & Logging

### Application Monitoring

```python
# Add Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    environment="production"
)
```

### Logging Setup

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'copilot.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

---

## Database Setup (Optional)

### PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE copilot_db;
CREATE USER copilot_user WITH PASSWORD 'strong_password';
ALTER ROLE copilot_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE copilot_db TO copilot_user;
\q
```

### Redis Cache

```bash
# Install Redis
sudo apt-get install redis-server

# Start service
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## Security Checklist

- [ ] HTTPS enabled (SSL certificates)
- [ ] CORS configured for specific domains
- [ ] API rate limiting implemented
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (if DB used)
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Logging and monitoring active
- [ ] Incident response plan documented

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# Database backup
pg_dump copilot_db > backup_$(date +%Y%m%d).sql

# Schedule with cron
0 2 * * * /path/to/backup_script.sh
```

### File Storage Backup

```bash
# Backup uploaded files
aws s3 sync /data/uploads s3://backup-bucket/
```

---

## Scaling Strategies

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
      
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing

```nginx
# nginx.conf
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location /api {
        proxy_pass http://backend;
    }
}
```

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy Backend
      run: |
        # Deploy to production
        
    - name: Deploy Frontend
      run: |
        # Deploy to production
```

---

## Troubleshooting

### Issue: API connection errors in production

**Solution:**
```bash
# Check CORS configuration
# Verify NEXT_PUBLIC_API_URL is set
# Check firewall rules
# Verify API server is running
```

### Issue: Slow LLM responses

**Solution:**
- Check Groq API quota
- Implement caching for repeated analyses
- Consider batch processing

### Issue: File upload failures

**Solution:**
```python
# Increase upload limits
app.add_middleware(
    MultipartFormDataHandler,
    max_size=50 * 1024 * 1024  # 50MB
)
```

### Issue: Database connection errors

**Solution:**
- Verify database is running
- Check connection string
- Verify credentials
- Check firewall rules

---

## Post-Deployment

### Health Checks

```bash
# Frontend
curl -I https://yourdomain.com

# Backend
curl https://api.yourdomain.com/health

# API Docs
curl https://api.yourdomain.com/docs
```

### Monitoring

```bash
# Check logs
docker-compose logs -f backend

# Monitor resources
docker stats

# Application monitoring
# Visit your Sentry/monitoring dashboard
```

### User Onboarding

1. Document API usage
2. Provide sample Excel workbook
3. Set up user authentication (if multi-user)
4. Configure provider communication
5. Schedule training/support

---

## Maintenance

### Regular Tasks

```bash
# Weekly
- Review error logs
- Monitor API usage
- Check backup integrity

# Monthly
- Update dependencies
- Security patches
- Performance review

# Quarterly
- Disaster recovery drill
- Capacity planning
- Feature updates
```

---

## Support & Resources

- **Documentation**: See README.md, ARCHITECTURE.md
- **API Docs**: `/docs` endpoint
- **Sample Data**: Run `generate_sample_workbook.py`
- **Issues**: Check troubleshooting section

## Next Steps

1. Choose deployment platform
2. Set up monitoring
3. Configure backups
4. Document runbooks
5. Train support team
6. Launch to production
