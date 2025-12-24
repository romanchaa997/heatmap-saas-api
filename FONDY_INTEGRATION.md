# Fondy Payment Gateway Integration

## Overview

Fondy is a leading Ukrainian payment gateway provider offering comprehensive SaaS payment processing solutions. This integration guide covers setting up Fondy for the Heatmap SaaS API.

**Provider**: Fondy (European subsidiary of PrivatBank Ukraine)
**Region**: Europe-focused with international payment support
**Commission**: Competitive rates starting from 2.5% for standard transactions

## Account Setup

### 1. Create Merchant Account

- Visit: https://fondy.ua/en/solutions/saas-service/
- Click "Зарегистрироваться" (Register)
- Enter email address
- Account will be created immediately with demo credentials

### 2. Merchant Credentials

**Merchant ID**: 1397120
**Portal**: https://portal.fondy.eu/mportal/

## Technical Integration

### API Documentation

Fondy provides comprehensive REST API documentation:
- **Endpoint**: https://api.fondy.eu/
- **Test Credentials**: Available at https://docs.fondy.eu/docs/page/2/
- **Main Operations**:
  - Checkout (Payment Form)
  - Recurring Payments (Subscriptions)
  - Refunds
  - Payment Status Verification

### Key API Parameters

```
merchant_id    - integer(12)   - Unique merchant identifier (required)
order_id       - string(1024)  - Unique order identifier (required)
signature      - string(40)    - HMAC-SHA1 signature for verification (required)
version        - string(10)    - API version (default: 1.0)
```

### Authentication

Fondy uses HMAC-SHA1 signature-based authentication:

```python
import hashlib

def generate_signature(merchant_id, api_key, order_id):
    msg = f"{merchant_id}|{order_id}|{api_key}"
    return hashlib.sha1(msg.encode()).hexdigest()
```

## Payment Methods Supported

✅ Credit/Debit Cards (Visa, MasterCard, etc.)
✅ Apple Pay
✅ Google Pay
✅ PrivatBank / Privat24 (Ukrainian users)
✅ Alternative payment methods (region-specific)
✅ Bank transfers
✅ E-wallets

## Integration Features

### 1. Payment Forms
- Hosted Payment Page (HPP) - Fondy-hosted checkout
- Embedded Checkout Widget
- Mobile-optimized forms
- Multi-currency support

### 2. Recurring Payments (SaaS)
- Subscription billing
- Trial period support
- Automatic renewal
- Flexible billing cycles

### 3. Webhooks
- Real-time payment notifications
- Supports multiple event types
- Configurable retry logic
- Security signature verification

### 4. Advanced Features
- Payment splitting (if enabled)
- Partial refunds
- 3D Secure authentication
- Fraud detection integration

## Dashboard Features

### Merchant Settings
- Technical Settings: `/mportal/#/settings/[merchant_id]/technical`
- API Keys management
- IP whitelisting for payouts
- Merchant name and website configuration

### Reporting & Analytics
- Real-time transaction dashboard
- Detailed settlement reports
- Tax reporting
- Payout history

### Available Modules in Portal
- **Платежи** (Payments) - Transaction management
- **Отчеты** (Reports) - Financial reporting
- **Инвойсы** (Invoices) - Invoice generation
- **Платежные кнопки** (Payment Buttons) - Quick pay links
- **Документация** (Documentation) - API docs

## Heatmap SaaS Integration Points

### 1. Subscription Management
```
Endpoint: POST /api/checkout/
Parameters:
- product: "Heatmap API Basic/Pro/Enterprise"
- price: "49.00" / "149.00" / "499.00" USD
- billing_cycle: "monthly" | "yearly"
- trial_days: 7
```

### 2. Webhook Handling
```
Webhook URL: https://api.heatmap.app/webhooks/fondy
Events:
- payment.success
- payment.failed
- subscription.renewed
- subscription.cancelled
```

### 3. Customer Portal
- Payment history view
- Invoice download
- Subscription management
- Payment method update

## Advantages of Fondy for Heatmap SaaS

✅ **European Compliance**: GDPR/PCI-DSS compliant
✅ **Ukrainian Payment Support**: Direct Privat24 integration
✅ **SaaS-Optimized**: Native subscription billing
✅ **Low Fees**: Competitive rates for high-volume
✅ **API-First**: Excellent documentation & SDKs
✅ **Multi-Currency**: Process payments in 150+ currencies
✅ **Global Payouts**: Settlement in UAH or USD to Ukrainian banks

## Testing

### Test Credentials
- **Mode**: Test mode enabled by default on demo account
- **Test Cards**: https://docs.fondy.eu/docs/page/2/
- **Webhook Testing**: Use postman or similar tools

### Test Workflow
1. Create test merchant (done: ID 1397120)
2. Set up webhook endpoint
3. Process test transactions
4. Verify webhook signatures
5. Test error handling

## Migration to Production

1. Submit merchant activation request
2. Provide company documentation:
   - Business registration
   - Owner identification
   - Bank account details
3. Manual review (1-3 business days)
4. Account activation
5. Switch from test to production API endpoints

## Comparison: Fondy vs Stripe vs LiqPay

| Feature | Fondy | Stripe | LiqPay |
|---------|-------|--------|--------|
| SaaS Focus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Ukrainian Support | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Global Reach | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Fee Structure | 2.5% | 2.9% + $0.30 | 2.75% |
| API Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Documentation | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## Resources

- **Portal**: https://portal.fondy.eu/
- **Documentation**: https://docs.fondy.eu/
- **API Reference**: https://docs.fondy.eu/docs/page/2/
- **Support**: support@fondy.ua
- **Status Page**: https://status.fondy.eu/

## Next Steps

1. ✅ Account created (ID: 1397120)
2. ⏳ Provide company information for activation
3. ⏳ Upload required documents
4. ⏳ Implement webhook handler
5. ⏳ Build subscription management UI
6. ⏳ Test payment flow end-to-end
7. ⏳ Go live with production credentials

---

**Last Updated**: December 24, 2025
**Integration Status**: Demo Account Active
**Environment**: Test/Sandbox
