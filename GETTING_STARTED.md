# Getting Started with Heatmap SaaS

## 🚀 Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/romanchaa997/heatmap-saas-api.git
cd heatmap-saas-api
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run the API
```bash
python main.py
```

The API is now running at `http://localhost:5000`

---

## 📋 Project Structure

```
heatmap-saas-api/
├── heatmap_orchestrator.py      # Core API engine
├── payment_processor.py         # Fondy integration
├── payment_tests.py            # Payment test suite
├── webhook_fondy.py            # Fondy webhook handler
├── customer_onboarding.py       # Customer lifecycle
├── email_service.py            # Email notifications
├── analytics_dashboard.py       # Analytics engine
├── affiliate_tracking.py        # Commission system
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker setup
├── Dockerfile                  # Container definition
├── README.md                   # Project overview
├── API_DOCUMENTATION.md        # API reference
├── LAUNCH_CHECKLIST.md         # Launch timeline
├── STRIPE_INTEGRATION.md       # Stripe setup
├── DEPLOYMENT.md               # Deployment guide
└── ... (10+ additional guides)
```

---

## 🔧 Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (optional, for Cloudflare)

### Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database Setup
```bash
# Create database
createdb heatmap_saas

# Run migrations (when available)
flask db upgrade
```

### Environment Variables
Create `.env` file with:
```bash
# API Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/heatmap_saas
REDIS_URL=redis://localhost:6379/0

# Payment Processing
FONDY_API_KEY=your_fondy_api_key
FONDY_MERCHANT_ID=1397120
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email Service
SENDGRID_API_KEY=your_sendgrid_key
EMAIL_FROM=noreply@heatmap-saas.com

# Cloudflare
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
```

---

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
pytest payment_tests.py -v
pytest test_webhook_fondy.py -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

---

## 📚 Documentation Guide

Read these files in order:

1. **README.md** - Project overview and features
2. **GETTING_STARTED.md** - This file, quick setup
3. **API_DOCUMENTATION.md** - Complete API reference
4. **DEPLOYMENT.md** - Production deployment guide
5. **LAUNCH_CHECKLIST.md** - Launch timeline and checklist
6. **STRIPE_INTEGRATION.md** - Stripe payment setup
7. **FONDY_INTEGRATION.md** - Fondy payment setup
8. **MONETIZATION_STRATEGY.md** - Business model

---

## 🏗️ Architecture Overview

### Core Components

**API Layer** (`main.py`)
- Flask/FastAPI compatible
- RESTful endpoints
- Authentication & authorization
- Rate limiting

**Payment Processing** (`payment_processor.py`)
- Fondy integration (live)
- Stripe integration (ready)
- Webhook handlers
- Transaction logging

**Analytics Engine** (`analytics_dashboard.py`)
- Real-time metrics
- Customer analytics
- Revenue tracking
- System health

**Affiliate System** (`affiliate_tracking.py`)
- Multi-tier commissions
- Click & conversion tracking
- Leaderboard functionality
- Payout processing

**Customer Management** (`customer_onboarding.py`)
- Account creation
- Subscription management
- Billing cycles
- Churn prevention

**Email Service** (`email_service.py`)
- Transactional emails
- Templates
- SendGrid integration
- Event triggers

### Infrastructure

**Deployment Options**
- Docker containers
- Kubernetes ready
- Cloudflare Workers
- AWS/GCP compatible

**Database**
- PostgreSQL (primary)
- Redis (cache/sessions)
- MongoDB ready (optional)

**Monitoring**
- 99.9% uptime tracking
- Error logging
- Performance metrics
- System health checks

---

## 🔐 Security Checklist

Before deployment:
- [ ] Change all default secrets
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable API key rotation
- [ ] Configure firewall rules
- [ ] Enable SQL parameterization
- [ ] Set up monitoring & alerts
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## 🚀 Deployment Quick Start

### Local Development
```bash
python main.py
```

### Docker
```bash
docker-compose up -d
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Cloudflare Workers
```bash
cd cloudflare-worker
wrangler publish
```

---

## 💡 Common Tasks

### Create an API Key
```python
from main import app, db
from models import APIKey

with app.app_context():
    key = APIKey.create(
        name="Development Key",
        permissions=["heatmaps.read", "heatmaps.write"]
    )
    db.session.add(key)
    db.session.commit()
    print(f"API Key: {key.token}")
```

### Test Payment Integration
```python
from payment_processor import FondyProcessor

processor = FondyProcessor()
result = processor.create_charge(
    amount=5000,
    currency="USD",
    description="Test charge"
)
print(result)
```

### Test Webhook
```bash
curl -X POST http://localhost:5000/webhook/fondy \
  -H "Content-Type: application/json" \
  -d '{"order_id": "123", "amount": 5000, "status": "success"}'
```

---

## 📞 Getting Help

### Documentation
- **API Docs**: See `API_DOCUMENTATION.md`
- **Deployment**: See `DEPLOYMENT.md`
- **Troubleshooting**: See `TROUBLESHOOTING.md` (coming soon)

### Community
- **Forum**: https://forum.heatmap-saas.com
- **Discord**: https://discord.gg/heatmap-saas
- **Email**: support@heatmap-saas.com

### Status
- **API Status**: https://status.heatmap-saas.com
- **GitHub Issues**: https://github.com/romanchaa997/heatmap-saas-api/issues

---

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/new-feature
```

### 2. Make Changes
```bash
# Edit files
# Write tests
# Update documentation
```

### 3. Run Tests
```bash
pytest
flake8 .
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: Add new feature"
```

### 5. Push and Create PR
```bash
git push origin feature/new-feature
```

---

## 🎯 Next Steps

1. **Read the docs**
   - API Documentation
   - Launch Checklist
   - Deployment Guide

2. **Set up development**
   - Clone repo
   - Install dependencies
   - Configure environment

3. **Run locally**
   - Start the API
   - Test endpoints
   - Check logs

4. **Deploy to production**
   - Follow deployment guide
   - Set up monitoring
   - Enable logging

5. **Launch business**
   - Create Fiverr gigs
   - Set up Stripe
   - Recruit affiliates

---

## 📈 Performance Tips

- Use Redis for session caching
- Enable database query optimization
- Implement CDN for static assets
- Use async workers for email
- Monitor API response times
- Set up rate limiting
- Regular database maintenance

---

## 🎓 Learning Resources

- **Python Guide**: https://python.readthedocs.io/
- **Flask Docs**: https://flask.palletsprojects.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/documentation
- **API Design**: https://swagger.io/

---

**Last Updated**: December 25, 2025  
**Status**: ✅ Production Ready  
**Questions?** Open an issue on GitHub or email support@heatmap-saas.com
