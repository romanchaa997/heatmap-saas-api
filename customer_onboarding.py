"""Customer Onboarding Module for Heatmap SaaS.

Handles:
- Customer registration and profile creation
- Service tier selection ($9, $49, $99)
- Payment method setup (Stripe/Fondy)
- Initial heatmap data ingestion
- Email confirmation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from datetime import datetime
import os
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
FONDY_MERCHANT_ID = os.getenv('FONDY_MERCHANT_ID', '1397120')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

app = FastAPI(title="Heatmap Onboarding API")

# Price tiers
PRICE_TIERS = {
    'starter': {'price': 9, 'currency': 'USD', 'requests_month': 100},
    'growth': {'price': 49, 'currency': 'USD', 'requests_month': 1000},
    'enterprise': {'price': 99, 'currency': 'USD', 'requests_month': 10000}
}


class CustomerProfile(BaseModel):
    """Customer onboarding data model."""
    email: EmailStr
    name: str
    company: Optional[str] = None
    location: dict  # {"lat": 40.7128, "lon": -74.0060}
    tier: str  # starter, growth, enterprise
    payment_method: str  # stripe or fondy
    

class OnboardingRequest(BaseModel):
    """Initial onboarding request."""
    profile: CustomerProfile
    callback_url: Optional[str] = None


class OnboardingService:
    """Handle customer onboarding process."""
    
    @staticmethod
    async def create_customer_account(profile: CustomerProfile) -> dict:
        """Create customer account and payment link."""
        logger.info(f"Creating account for {profile.email}")
        
        tier_info = PRICE_TIERS.get(profile.tier)
        if not tier_info:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        # Create payment payload
        if profile.payment_method == 'fondy':
            payment_data = {
                'merchant_id': FONDY_MERCHANT_ID,
                'order_id': f"HEATMAP-{profile.email}-{int(datetime.now().timestamp())}",
                'order_amount': int(tier_info['price'] * 100),  # cents
                'order_currency': tier_info['currency'],
                'order_desc': f"Heatmap {profile.tier.title()} Plan",
                'customer_email': profile.email,
                'customer_data': {
                    'name': profile.name,
                    'company': profile.company,
                    'location': profile.location
                }
            }
            return {
                'status': 'payment_initiated',
                'payment_provider': 'fondy',
                'order_id': payment_data['order_id'],
                'amount': tier_info['price'],
                'currency': tier_info['currency'],
                'tier': profile.tier,
                'requests_included': tier_info['requests_month']
            }
        
        elif profile.payment_method == 'stripe':
            # Stripe integration
            return {
                'status': 'payment_initiated',
                'payment_provider': 'stripe',
                'amount': tier_info['price'],
                'currency': tier_info['currency'],
                'tier': profile.tier,
                'requests_included': tier_info['requests_month']
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid payment method")
    
    @staticmethod
    async def send_confirmation_email(email: str, profile: CustomerProfile) -> bool:
        """Send onboarding confirmation email via SendGrid."""
        logger.info(f"Sending confirmation email to {email}")
        
        # Email template
        email_content = f"""
        <h2>Welcome to Heatmap SaaS!</h2>
        <p>Hi {profile.name},</p>
        <p>Your account has been created successfully.</p>
        <p><strong>Plan Details:</strong></p>
        <ul>
            <li>Tier: {profile.tier.title()}</li>
            <li>Price: ${PRICE_TIERS[profile.tier]['price']}/month</li>
            <li>Monthly Requests: {PRICE_TIERS[profile.tier]['requests_month']}</li>
        </ul>
        <p><strong>API Endpoint:</strong></p>
        <code>https://still-band-434fheatmap-saas-api.romanchaa997.workers.dev/api/heatmap</code>
        <p>Start integrating now!</p>
        """
        
        # TODO: Implement actual SendGrid sending
        logger.info(f"Email template prepared for {email}")
        return True


@app.post('/api/onboard')
async def onboard_customer(request: OnboardingRequest, background_tasks: BackgroundTasks):
    """Customer onboarding endpoint.
    
    POST /api/onboard
    {
        "profile": {
            "email": "customer@example.com",
            "name": "John Doe",
            "company": "TechCorp",
            "location": {"lat": 40.7128, "lon": -74.0060},
            "tier": "growth",
            "payment_method": "fondy"
        },
        "callback_url": "https://yourapp.com/webhook"
    }
    
    Returns payment link and account details.
    """
    try:
        # Validate tier
        if request.profile.tier not in PRICE_TIERS:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        # Create account and initiate payment
        account_info = await OnboardingService.create_customer_account(request.profile)
        
        # Send confirmation email in background
        background_tasks.add_task(
            OnboardingService.send_confirmation_email,
            request.profile.email,
            request.profile
        )
        
        logger.info(f"Onboarding completed for {request.profile.email}")
        
        return {
            'status': 'success',
            'message': 'Onboarding initiated',
            'account_info': account_info,
            'api_endpoint': 'https://still-band-434fheatmap-saas-api.romanchaa997.workers.dev/api/heatmap',
            'dashboard': 'https://still-band-434fheatmap-saas-api.romanchaa997.workers.dev/dashboard',
            'created_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Onboarding error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/pricing')
async def get_pricing():
    """Get available pricing tiers."""
    return {
        'tiers': PRICE_TIERS,
        'description': 'Choose the plan that fits your needs'
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8002)
