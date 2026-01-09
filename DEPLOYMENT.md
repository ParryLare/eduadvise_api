# Deployment Guide

This guide covers deploying the EduAdvise API to various platforms.

## Table of Contents
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Production Checklist](#production-checklist)
- [Environment Setup](#environment-setup)

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=eduadvise
      - JWT_SECRET=${JWT_SECRET}
      - LOG_LEVEL=INFO
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - mongodb
    restart: unless-stopped
    
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d
    environment:
      - MONGO_INITDB_DATABASE=eduadvise
    restart: unless-stopped

volumes:
  mongodb_data:
```

### 3. Build and Run

```bash
# Build the image
docker-compose build

# Run the containers
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop containers
docker-compose down
```

## Cloud Platforms

### AWS (Elastic Beanstalk)

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize EB**:
```bash
eb init -p python-3.10 eduadvise-api --region us-east-1
```

3. **Create environment**:
```bash
eb create eduadvise-api-prod
```

4. **Set environment variables**:
```bash
eb setenv MONGO_URL=your-mongo-url DB_NAME=eduadvise JWT_SECRET=your-secret
```

5. **Deploy**:
```bash
eb deploy
```

### Google Cloud Platform (Cloud Run)

1. **Build and push image**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/eduadvise-api
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy eduadvise-api \
  --image gcr.io/PROJECT_ID/eduadvise-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MONGO_URL=your-mongo-url,DB_NAME=eduadvise,JWT_SECRET=your-secret
```

### Heroku

1. **Create app**:
```bash
heroku create eduadvise-api
```

2. **Add MongoDB addon**:
```bash
heroku addons:create mongolab:sandbox
```

3. **Set environment variables**:
```bash
heroku config:set JWT_SECRET=your-secret
```

4. **Create Procfile**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. **Deploy**:
```bash
git push heroku main
```

### DigitalOcean App Platform

1. **Create app.yaml**:
```yaml
name: eduadvise-api
services:
- name: api
  github:
    repo: your-username/eduadvise-api
    branch: main
    deploy_on_push: true
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_size_slug: basic-xxs
  instance_count: 1
  http_port: 8080
  envs:
  - key: MONGO_URL
    value: ${db.DATABASE_URL}
  - key: DB_NAME
    value: eduadvise
  - key: JWT_SECRET
    type: SECRET
    value: your-secret-key

databases:
- name: db
  engine: MONGODB
  version: "7"
```

2. **Deploy via doctl**:
```bash
doctl apps create --spec app.yaml
```

## Production Checklist

### Security
- [ ] Change `JWT_SECRET` to a strong, random value (minimum 32 characters)
- [ ] Use strong database password
- [ ] Enable SSL/TLS for database connections
- [ ] Configure CORS to only allow specific origins
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS for API endpoints

### Performance
- [ ] Set up database indexes (see README)
- [ ] Configure connection pooling
- [ ] Enable caching where appropriate
- [ ] Set up CDN for static files
- [ ] Configure worker count based on CPU cores
- [ ] Monitor memory usage

### Monitoring
- [ ] Set up application logging
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring
- [ ] Set up database monitoring
- [ ] Create dashboards for key metrics

### Backup & Recovery
- [ ] Configure automated database backups
- [ ] Test restore procedures
- [ ] Set up file storage backups
- [ ] Document recovery procedures

### Scalability
- [ ] Configure horizontal scaling
- [ ] Set up load balancing
- [ ] Implement caching strategy
- [ ] Configure auto-scaling rules
- [ ] Optimize database queries

## Environment Setup

### Production Environment Variables

```env
# Application
APP_NAME=EduAdvise API
DEBUG=False
API_PREFIX=/api
LOG_LEVEL=WARNING

# Database
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/
DB_NAME=eduadvise_prod

# Security
JWT_SECRET=<generate-strong-random-secret-min-32-chars>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# CORS
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# File Upload
MAX_FILE_SIZE=10485760

# External Services
GOOGLE_CALENDAR_CLIENT_ID=your-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-client-secret
```

### Generating Secure Secrets

```python
# Generate JWT secret
import secrets
print(secrets.token_urlsafe(32))
```

Or use command line:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## TURN Server Setup

For production video/audio calls, you need a TURN server:

### Using Coturn (Self-hosted)

1. **Install Coturn**:
```bash
sudo apt-get update
sudo apt-get install coturn
```

2. **Configure** (`/etc/turnserver.conf`):
```
listening-port=3478
fingerprint
lt-cred-mech
user=username:password
realm=yourdomain.com
```

3. **Start service**:
```bash
sudo systemctl start coturn
sudo systemctl enable coturn
```

### Using Cloud TURN Services

- **Twilio Network Traversal Service**: https://www.twilio.com/stun-turn
- **Xirsys**: https://xirsys.com/
- **Metered TURN**: https://www.metered.ca/tools/openrelay/

## Monitoring & Logging

### Using Sentry for Error Tracking

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Using Prometheus for Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

1. **Install Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Get certificate**:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Nginx config**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Database Migration

If migrating from the old server.py structure:

1. **Export existing data**:
```bash
mongodump --uri="mongodb://localhost:27017/old_db" --out=backup
```

2. **Import to new database**:
```bash
mongorestore --uri="mongodb://localhost:27017/eduadvise" backup/old_db/
```

3. **Verify data**:
```bash
mongo eduadvise --eval "db.users.count()"
```

## Troubleshooting

### Common Issues

**Issue**: Application won't start
- Check MongoDB connection
- Verify all environment variables are set
- Check logs: `docker-compose logs api`

**Issue**: WebSocket connections failing
- Verify firewall allows WebSocket connections
- Check proxy configuration for WebSocket support
- Enable WebSocket in load balancer settings

**Issue**: File uploads failing
- Check uploads directory permissions
- Verify MAX_FILE_SIZE setting
- Check available disk space

## Support

For deployment support, contact: devops@eduadvise.com
