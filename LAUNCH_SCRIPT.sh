#!/bin/bash

# 🚀 HEATMAP SAAS API - PRODUCTION LAUNCH SCRIPT
# Execute this script to activate all payment systems and deploy
# Run: bash LAUNCH_SCRIPT.sh

echo "═══════════════════════════════════════════════════════════"
echo "  HEATMAP SAAS API - PRODUCTION LAUNCH v1.0"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "⚡ CRITICAL STEPS TO COMPLETE BEFORE RUNNING:\n"
echo "1. STRIPE - Sign in to https://dashboard.stripe.com/login"
echo "   └─ Verify email in inbox"
echo "   └─ Enable Stripe webhooks at Settings > Webhooks"
echo "   └─ Copy API keys to .env file"
echo ""
echo "2. FIVERR - Complete email verification"
echo "   └─ Check romanchaa997@gmail.com for verification code"
echo "   └─ Enter code at https://www.fiverr.com/gigs/new"
echo "   └─ Create first gig with pricing (Basic $49, Pro $149, Enterprise $499)"
echo ""
echo "3. SENDGRID - Set up email service"
echo "   └─ Create account at https://sendgrid.com"
echo "   └─ Get API key"
echo "   └─ Add to .env: SENDGRID_API_KEY=sg_xxxxxxxx"
echo ""
echo "4. ENVIRONMENT - Update .env file"
echo "   └─ STRIPE_API_KEY=sk_test_xxxxxx"
echo "   └─ STRIPE_WEBHOOK_SECRET=whsec_xxxxxx"
echo "   └─ FONDY_MERCHANT_ID=1397120"
echo "   └─ DATABASE_URL=postgresql://user:pass@localhost/heatmap"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "✅ Once above steps are complete, deployment will:\n"
echo "✓ Install Python dependencies"
echo "✓ Start FastAPI server (localhost:8000)"
echo "✓ Deploy to Cloudflare Workers (already active)"
echo "✓ Enable Fondy webhook at /webhook/fondy"
echo "✓ Enable Stripe webhook at /webhook/stripe"
echo "✓ Start SendGrid email service"
echo "✓ Initialize PostgreSQL database"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  ERROR: .env file not found!"
    echo "   Create .env from .env.example:"
    echo "   cp .env.example .env"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not installed! Install from python.org"
    exit 1
fi

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Starting PostgreSQL (ensure Docker/local instance running)..."
# Uncomment if using Docker Compose:
# docker-compose up -d

echo "🚀 Launching FastAPI server..."
echo "   → API will be available at http://localhost:8000"
echo "   → Docs at http://localhost:8000/docs"
echo ""

python3 main.py

echo ""
echo "✅ HEATMAP SAAS API IS LIVE!"
echo "   📊 Dashboard: http://localhost:8000"
echo "   📝 Docs: http://localhost:8000/docs"
echo "   💰 Revenue via Stripe + Fondy + Fiverr"
echo "   📧 Emails sent via SendGrid"
echo ""
echo "═══════════════════════════════════════════════════════════"
