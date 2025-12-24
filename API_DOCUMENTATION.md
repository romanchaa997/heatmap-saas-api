# Heatmap SaaS API Documentation

## Overview

The Heatmap SaaS API provides comprehensive location-based analytics and heatmap visualization capabilities for businesses. This document covers all available endpoints, authentication methods, and integration examples.

## Base URL

```
Production: https://api.heatmap-saas.com/v1
Staging: https://staging-api.heatmap-saas.com/v1
```

## Authentication

All API requests require authentication using API keys. Include your API key in the request header:

```bash
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Getting Your API Key

1. Create an account at https://heatmap-saas.com
2. Navigate to Settings > API Keys
3. Generate a new API key
4. Copy the key (it won't be shown again)

## Rate Limiting

- Free tier: 100 requests/hour
- Pro tier: 10,000 requests/hour
- Enterprise: Unlimited

Rate limit headers included in response:
```
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9999
X-RateLimit-Reset: 1735128000
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required parameter: location_id",
    "details": {
      "parameter": "location_id",
      "type": "required"
    }
  }
}
```

## API Endpoints

### Heatmaps

#### Create Heatmap
```
POST /heatmaps
```

**Request:**
```json
{
  "name": "Store A - Customer Flow",
  "location_id": "loc_123456",
  "type": "customer_flow",
  "timezone": "America/Los_Angeles",
  "refresh_interval": 3600
}
```

**Response:**
```json
{
  "id": "hm_789",
  "name": "Store A - Customer Flow",
  "location_id": "loc_123456",
  "type": "customer_flow",
  "created_at": "2025-12-25T00:00:00Z",
  "status": "active"
}
```

#### Get Heatmap Data
```
GET /heatmaps/{heatmap_id}/data
```

**Query Parameters:**
- `start_date` (required): ISO 8601 date
- `end_date` (required): ISO 8601 date
- `granularity` (optional): hour, day, week (default: hour)

**Response:**
```json
{
  "heatmap_id": "hm_789",
  "data_points": [
    {
      "timestamp": "2025-12-25T12:00:00Z",
      "x": 150,
      "y": 200,
      "intensity": 0.85
    }
  ],
  "summary": {
    "total_visitors": 5000,
    "peak_hour": 14,
    "busiest_day": "Saturday"
  }
}
```

### Locations

#### Create Location
```
POST /locations
```

**Request:**
```json
{
  "name": "Store A - Main Branch",
  "address": "1 Battery Street, San Francisco, CA 94111",
  "latitude": 37.7922,
  "longitude": -122.3942,
  "type": "retail",
  "timezone": "America/Los_Angeles"
}
```

**Response:**
```json
{
  "id": "loc_123456",
  "name": "Store A - Main Branch",
  "address": "1 Battery Street, San Francisco, CA 94111",
  "latitude": 37.7922,
  "longitude": -122.3942,
  "type": "retail",
  "created_at": "2025-12-25T00:00:00Z"
}
```

#### List Locations
```
GET /locations
```

**Query Parameters:**
- `limit` (optional): 1-100 (default: 20)
- `offset` (optional): For pagination
- `type` (optional): Filter by location type

**Response:**
```json
{
  "locations": [
    {
      "id": "loc_123456",
      "name": "Store A - Main Branch",
      "type": "retail",
      "heatmaps_count": 3
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 20,
    "offset": 0
  }
}
```

### Analytics

#### Get Location Analytics
```
GET /locations/{location_id}/analytics
```

**Query Parameters:**
- `start_date` (required): ISO 8601 date
- `end_date` (required): ISO 8601 date
- `metrics` (optional): comma-separated list (visitors,duration,conversion)

**Response:**
```json
{
  "location_id": "loc_123456",
  "period": {
    "start": "2025-12-18T00:00:00Z",
    "end": "2025-12-25T00:00:00Z"
  },
  "metrics": {
    "visitors": 45000,
    "avg_duration_minutes": 23,
    "conversion_rate": 0.12,
    "peak_hours": [11, 12, 14, 15, 18]
  },
  "daily_breakdown": [
    {
      "date": "2025-12-25",
      "visitors": 5000,
      "avg_duration_minutes": 22
    }
  ]
}
```

### Payments

#### Create Payment Intent
```
POST /payments/intent
```

**Request:**
```json
{
  "amount": 9999,
  "currency": "USD",
  "customer_id": "cust_123",
  "plan_id": "plan_pro",
  "description": "Pro Plan - Monthly Subscription"
}
```

**Response:**
```json
{
  "intent_id": "pi_123456",
  "client_secret": "pi_123456_secret_abcdef",
  "amount": 9999,
  "currency": "USD",
  "status": "requires_payment_method"
}
```

#### Confirm Payment
```
POST /payments/{intent_id}/confirm
```

**Request:**
```json
{
  "payment_method_id": "pm_123456"
}
```

**Response:**
```json
{
  "intent_id": "pi_123456",
  "status": "succeeded",
  "transaction_id": "txn_123456",
  "amount": 9999,
  "currency": "USD"
}
```

### Webhooks

#### Register Webhook
```
POST /webhooks
```

**Request:**
```json
{
  "url": "https://your-domain.com/webhooks/heatmap",
  "events": ["heatmap.data_updated", "payment.succeeded"],
  "active": true
}
```

**Response:**
```json
{
  "id": "webhook_123",
  "url": "https://your-domain.com/webhooks/heatmap",
  "events": ["heatmap.data_updated", "payment.succeeded"],
  "secret": "whsec_abc123def456",
  "created_at": "2025-12-25T00:00:00Z"
}
```

#### Webhook Events

**heatmap.created**
```json
{
  "event": "heatmap.created",
  "timestamp": "2025-12-25T12:00:00Z",
  "data": {
    "heatmap_id": "hm_789",
    "location_id": "loc_123456",
    "name": "Store A - Customer Flow"
  }
}
```

**heatmap.data_updated**
```json
{
  "event": "heatmap.data_updated",
  "timestamp": "2025-12-25T13:00:00Z",
  "data": {
    "heatmap_id": "hm_789",
    "new_data_points": 1250,
    "last_update": "2025-12-25T12:59:00Z"
  }
}
```

**payment.succeeded**
```json
{
  "event": "payment.succeeded",
  "timestamp": "2025-12-25T12:00:00Z",
  "data": {
    "intent_id": "pi_123456",
    "transaction_id": "txn_123456",
    "amount": 9999,
    "customer_id": "cust_123"
  }
}
```

## Code Examples

### Python

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://api.heatmap-saas.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create a heatmap
response = requests.post(
    f"{BASE_URL}/heatmaps",
    json={
        "name": "Store A - Customer Flow",
        "location_id": "loc_123456",
        "type": "customer_flow"
    },
    headers=headers
)

heatmap = response.json()
print(f"Created heatmap: {heatmap['id']}")

# Get heatmap data
response = requests.get(
    f"{BASE_URL}/heatmaps/{heatmap['id']}/data",
    params={
        "start_date": "2025-12-18",
        "end_date": "2025-12-25"
    },
    headers=headers
)

data = response.json()
print(f"Total visitors: {data['summary']['total_visitors']}")
```

### JavaScript

```javascript
const API_KEY = "your_api_key_here";
const BASE_URL = "https://api.heatmap-saas.com/v1";

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
};

// Create a heatmap
const createHeatmap = async () => {
  const response = await fetch(`${BASE_URL}/heatmaps`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      name: "Store A - Customer Flow",
      location_id: "loc_123456",
      type: "customer_flow"
    })
  });
  
  const heatmap = await response.json();
  return heatmap;
};

// Get heatmap data
const getHeatmapData = async (heatmapId) => {
  const response = await fetch(
    `${BASE_URL}/heatmaps/${heatmapId}/data?start_date=2025-12-18&end_date=2025-12-25`,
    { headers }
  );
  
  const data = await response.json();
  return data;
};
```

## Best Practices

1. **Cache API responses** where appropriate to reduce API calls
2. **Use webhooks** instead of polling for real-time updates
3. **Implement exponential backoff** for retry logic
4. **Monitor rate limits** and adjust your request frequency
5. **Use batch endpoints** when available for better performance
6. **Validate webhook signatures** to ensure authenticity
7. **Store API keys securely** in environment variables
8. **Use pagination** for large result sets

## Support

- **Documentation**: https://docs.heatmap-saas.com
- **API Status**: https://status.heatmap-saas.com
- **Support Email**: api-support@heatmap-saas.com
- **Community Forum**: https://forum.heatmap-saas.com

---

**Last Updated**: December 25, 2025
**API Version**: v1
**Status**: Production Ready
