# Heatmap SaaS API - Deployment Guide

## Production Deployment

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+
- Google AI API Key
- Stripe API Keys

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Local Development

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Docker Deployment

```bash
docker-compose up -d
```

### AWS EC2 Deployment

1. Launch Ubuntu 22.04 instance
2. Install Docker:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```
3. Clone repository and deploy
4. Configure SSL with Let's Encrypt

### Database Migrations

```bash
alembic upgrade head
```

### Health Check

```bash
curl http://localhost:8000/health
```
