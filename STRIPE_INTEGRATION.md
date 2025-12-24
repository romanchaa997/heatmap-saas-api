# Stripe Integration Guide for Heatmap SaaS

## Overview

This guide provides step-by-step instructions for integrating Stripe payment processing into Heatmap SaaS as a secondary payment gateway alongside Fondy.

## Why Stripe?

- Industry-standard payment processor
- Better US market coverage
- Comprehensive webhook system
- Excellent documentation and SDKs
- Lower fees than Fondy for US transactions
- Supports multiple payment methods (cards, ACH, Apple Pay)

## Registration & Setup

### Step 1: Create Stripe Account

1. Navigate to: https://dashboard.stripe.com/register
2. Enter email: romanchaa997@gmail.com
3. Create strong password
4. Agree to terms and register
5. Complete email verification

### Step 2: Complete Business Information

1. Login to Stripe Dashboard
2. Navigate to Settings > Account Settings
3. Fill in business details:
   - Legal Business Name: Heatmap SaaS Inc
   - Business Type: Technology/Software
   - Website: https://api.heatmap-saas.com
   - Business Address: 1 Battery Street, San Francisco, CA
   - Phone: +1 (555) 123-4567

### Step 3: Verify Identity

1. Upload government-issued ID
2. Provide verification documents
3. Wait for approval (typically 1-3 business days)

### Step 4: Configure Payouts

1. Navigate to Settings > Bank Accounts
2. Add bank account for receiving payouts
3. Set minimum payout amount
4. Enable automatic payouts

## API Keys

### Get Your Keys

1. Login to Stripe Dashboard
2. Navigate to Developers > API Keys
3. Copy the following:
   - **Publishable Key**: `pk_live_...` (for client-side)
   - **Secret Key**: `sk_live_...` (for server-side, KEEP SECRET)
   - **Webhook Secret**: Generated after webhook setup

### Store Securely

```bash
# In your .env file (NEVER commit this)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Payment Processor Implementation

### Create payment_processor_stripe.py

```python
import stripe
import os
from datetime import datetime
from typing import Dict, Optional

class StripePaymentProcessor:
    def __init__(self):
        self.stripe_key = os.getenv('STRIPE_SECRET_KEY')
        stripe.api_key = self.stripe_key
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    def create_payment_intent(self, amount: float, currency: str = 'usd',
                           customer_id: str = None, 
                           metadata: Dict = None) -> Dict:
        """
        Create a Stripe PaymentIntent for the given amount.
        
        Args:
            amount: Amount in cents (e.g., 5000 for $50.00)
            currency: 3-letter currency code
            customer_id: Optional Stripe customer ID
            metadata: Optional metadata dict
        
        Returns:
            Dict with client_secret and payment_intent_id
        """
        try:
            intent_data = {
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            if metadata:
                intent_data['metadata'] = metadata
            
            intent = stripe.PaymentIntent.create(**intent_data)
            
            return {
                'status': 'success',
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': currency
            }
        except stripe.error.CardError as e:
            return {'status': 'error', 'error': str(e), 'error_code': e.code}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def confirm_payment(self, payment_intent_id: str) -> Dict:
        """
        Retrieve and confirm payment intent status.
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'status': intent.status,
                'amount': intent.amount / 100,
                'currency': intent.currency,
                'payment_method': intent.payment_method,
                'charges': len(intent.charges.data) > 0
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def create_customer(self, email: str, name: str = None,
                       description: str = None) -> Dict:
        """
        Create a Stripe customer for recurring billing.
        """
        try:
            customer_data = {'email': email}
            if name:
                customer_data['name'] = name
            if description:
                customer_data['description'] = description
            
            customer = stripe.Customer.create(**customer_data)
            return {
                'status': 'success',
                'customer_id': customer.id,
                'email': customer.email
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def create_subscription(self, customer_id: str, plan_id: str) -> Dict:
        """
        Create a recurring subscription for a customer.
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': plan_id}]
            )
            return {
                'status': 'success',
                'subscription_id': subscription.id,
                'status': subscription.status
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def process_refund(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict:
        """
        Process a refund for a payment.
        """
        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            return {
                'status': 'success',
                'refund_id': refund.id,
                'amount': refund.amount / 100
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
```

## Webhook Configuration

### 1. Set Up Webhook Endpoint

Add to your Cloudflare Workers (stripe_webhook_handler.js):

```javascript
export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname === '/webhooks/stripe') {
      const signature = request.headers.get('stripe-signature');
      const body = await request.text();
      
      try {
        // Verify webhook signature
        const event = verifyStripeSignature(body, signature, env.STRIPE_WEBHOOK_SECRET);
        
        // Handle different event types
        switch(event.type) {
          case 'payment_intent.succeeded':
            await handlePaymentSuccess(event.data.object);
            break;
          case 'payment_intent.payment_failed':
            await handlePaymentFailed(event.data.object);
            break;
          case 'charge.refunded':
            await handleRefund(event.data.object);
            break;
          case 'customer.subscription.updated':
            await handleSubscriptionUpdate(event.data.object);
            break;
        }
        
        return new Response(JSON.stringify({received: true}), {status: 200});
      } catch (err) {
        return new Response('Invalid signature', {status: 400});
      }
    }
    return new Response('Not Found', {status: 404});
  }
};
```

### 2. Register Webhook in Stripe Dashboard

1. Navigate to Developers > Webhooks
2. Click "Add endpoint"
3. Enter Endpoint URL: `https://still-band-434fheatmap-saas-api.romanchaa997.workers.dev/webhooks/stripe`
4. Select events:
   - payment_intent.succeeded
   - payment_intent.payment_failed
   - charge.refunded
   - customer.subscription.updated
5. Get and save Webhook Secret

## Testing

### Test Credentials

Stripe provides test card numbers:

- **Visa Success**: 4242 4242 4242 4242
- **Visa Decline**: 4000 0000 0000 0002
- **Amex**: 3782 822463 10005
- **Exp Date**: Any future date (e.g., 12/25)
- **CVC**: Any 3-digit number

### Test Webhook

```bash
# Using Stripe CLI for local testing
stripe listen --forward-to localhost:5000/webhooks/stripe
stripe trigger payment_intent.succeeded
```

## Monitoring

### Payment Dashboard

1. Login to Stripe Dashboard
2. Navigate to Payments
3. View all transactions
4. Filter by status, date, amount
5. View customer details

### Failed Payments Alert

Set up Stripe alerts:
1. Developers > Events
2. Enable email alerts for:
   - payment_intent.payment_failed
   - charge.dispute.created

## Security Best Practices

1. **Never expose Secret Key**: Keep in environment variables
2. **Use HTTPS**: All payments must be over HTTPS
3. **Validate Webhooks**: Always verify webhook signatures
4. **PCI Compliance**: Never store card data locally
5. **Rate Limiting**: Implement rate limits on payment endpoints
6. **Logging**: Log all payment transactions (without sensitive data)

## Troubleshooting

### Issue: PaymentIntent fails
- Check webhook signature verification
- Verify API keys are correct
- Check amount is in cents
- Ensure customer exists if using customer_id

### Issue: Webhooks not received
- Verify endpoint URL is correct
- Check webhook secret
- Review Stripe Dashboard > Events > Deliveries
- Check server logs for errors

### Issue: Refund fails
- Ensure payment is fully captured
- Check refund amount doesn't exceed original
- Verify payment status is succeeded

## Support

- **Stripe Docs**: https://stripe.com/docs
- **API Reference**: https://stripe.com/docs/api
- **Support Email**: support@stripe.com
- **Status Page**: https://status.stripe.com

## Next Steps

1. [ ] Create Stripe account
2. [ ] Get API keys
3. [ ] Implement payment_processor_stripe.py
4. [ ] Deploy webhook handler
5. [ ] Test with test cards
6. [ ] Go live with production keys
7. [ ] Monitor payments

---

**Last Updated**: December 25, 2025
**Integration Status**: Ready for Implementation
