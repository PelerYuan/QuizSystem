# 🚀 High-Performance Docker Deployment Guide

## 📋 Overview

This deployment provides a production-ready, high-performance setup for the Quiz System using Docker and Docker Compose with the following optimizations:

### 🏗️ Architecture

```
Internet → Nginx (Reverse Proxy) → Gunicorn (WSGI) → Flask App
                ↓
        Static Files & Media
                ↓
        Redis (Caching) → SQLite/PostgreSQL
```

### 🎯 Performance Features

- **Multi-stage Docker build** for minimal image size
- **Nginx reverse proxy** with gzip compression and static file serving
- **Gunicorn WSGI server** with optimized worker configuration
- **Redis caching** for session management
- **Health checks** for all services
- **Rate limiting** and security headers
- **Persistent volumes** for data retention

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 1GB RAM
- 2GB available disk space

### 1. Initial Setup

```bash
# Clone and navigate to the project
cd QuizSystem

# Copy environment template
cp .env.example .env

# Edit configuration (important!)
nano .env
```

### 2. Deploy with Script

```bash
# Make script executable
chmod +x deploy.sh

# Deploy in production mode
./deploy.sh prod --build

# Or deploy in development mode
./deploy.sh dev --build --logs
```

### 3. Manual Deployment

```bash
# Create environment file
cp .env.example .env

# Start services
docker-compose up -d --build

# Check status
docker-compose ps
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Application
FLASK_ENV=production
ADMIN_PASSWORD=your_secure_password

# Database (optional PostgreSQL upgrade)
POSTGRES_PASSWORD=secure_postgres_password

# Security
SECRET_KEY=your_32_character_secret_key

# Performance
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=30
```

### Scaling Configuration

```bash
# Scale application instances
docker-compose up -d --scale quiz-app=3

# Scale with more memory
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost/health

# Check all service status
docker-compose ps
```

### Log Management

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f quiz-app
docker-compose logs -f nginx

# Follow logs in real-time
docker-compose logs -f --tail=100
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Service metrics
docker-compose exec quiz-app top
```

## 🔄 Database Operations

### Backup

```bash
# SQLite backup
docker-compose exec quiz-app cp /app/data.sqlite /app/data/backup-$(date +%Y%m%d).sqlite

# PostgreSQL backup (if using)
docker-compose exec postgres pg_dump -U quizuser quizdb > backup.sql
```

### Restore

```bash
# SQLite restore
docker-compose exec quiz-app cp /app/data/backup.sqlite /app/data.sqlite

# PostgreSQL restore
docker-compose exec -T postgres psql -U quizuser quizdb < backup.sql
```

## 🛡️ Security Hardening

### 1. SSL/TLS Setup

```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Update nginx.conf to enable HTTPS section
# Update docker-compose.yml to mount certificates
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # Block direct app access
```

### 3. Regular Updates

```bash
# Update base images
docker-compose pull
docker-compose up -d --build
```

## ⚡ Performance Optimization

### 1. Resource Limits

```yaml
# In docker-compose.yml
services:
  quiz-app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### 2. Nginx Tuning

```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
```

### 3. Gunicorn Tuning

```python
# In gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # For I/O intensive workloads
worker_connections = 1000
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
docker-compose logs quiz-app

# Check file permissions
docker-compose exec quiz-app ls -la /app

# Rebuild without cache
docker-compose build --no-cache quiz-app
```

#### Database Connection Issues

```bash
# Check database file
docker-compose exec quiz-app ls -la /app/data.sqlite

# Check volume mounts
docker volume ls
docker volume inspect quiz_data
```

#### Performance Issues

```bash
# Check resource usage
docker stats --no-stream

# Check worker processes
docker-compose exec quiz-app ps aux

# Monitor response times
curl -w "@curl-format.txt" -s -o /dev/null http://localhost/
```

#### Memory Issues

```bash
# Check memory usage
docker-compose exec quiz-app free -h

# Restart services to clear memory
docker-compose restart
```

## 📈 Advanced Features

### 1. Load Balancing

```yaml
# docker-compose.scale.yml
services:
  quiz-app:
    scale: 3

  nginx:
    volumes:
      - ./nginx-lb.conf:/etc/nginx/conf.d/default.conf
```

### 2. Database Upgrade to PostgreSQL

```bash
# Uncomment PostgreSQL service in docker-compose.yml
# Update app.py database configuration
# Migrate existing data
```

### 3. Monitoring Stack

```bash
# Enable Prometheus and Grafana
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

## 🔗 Useful Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart quiz-app

# View service logs
docker-compose logs -f quiz-app

# Execute commands in container
docker-compose exec quiz-app bash

# Scale services
docker-compose up -d --scale quiz-app=3

# Update and restart
docker-compose pull && docker-compose up -d

# Clean up unused resources
docker system prune -a
```

## 📞 Support

For issues related to the Docker deployment:

1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Check resource usage: `docker stats`
4. Review health checks: `curl http://localhost/health`

## 🔄 Updates and Maintenance

### Regular Maintenance Schedule

- **Weekly**: Check logs and resource usage
- **Monthly**: Update base images and restart services
- **Quarterly**: Review security settings and backup procedures

### Update Process

```bash
# Pull latest images
docker-compose pull

# Backup current data
./backup.sh

# Deploy updates
docker-compose up -d --build

# Verify deployment
curl http://localhost/health
```