"""Fondy Payment Webhook Handler for Heatmap SaaS API.

Handles incoming Fondy payment notifications for:
- Payment success/failure callbacks
- Subscription updates
- Refund processing
"""

import os
import hmac
import hashlib
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

FONDY_MERCHANT_ID = os.getenv('FONDY_MERCHANT_ID', '1397120')
FONDY_API_KEY = os.getenv('FONDY_API_KEY', '')


class FondyWebhookHandler:
    """Handle Fondy payment gateway webhooks."""

    @staticmethod
    def verify_signature(data: dict, signature: str) -> bool:
        """Verify Fondy webhook signature.
        
        Args:
            data: Webhook payload
            signature: HMAC signature from Fondy
            
        Returns:
            bool: True if signature is valid
        """
        # Create signature string from payment fields
        merchant_id = data.get('merchant_id')
        order_id = data.get('order_id')
        order_amount = data.get('order_amount')
        order_currency = data.get('order_currency')
        order_status = data.get('order_status')
        response_signature_string = f"{merchant_id};{order_id};{order_amount};{order_currency};{order_status};{FONDY_API_KEY}"
        
        # Calculate HMAC-MD5
        expected_signature = hmac.new(
            FONDY_API_KEY.encode(),
            response_signature_string.encode(),
            hashlib.md5
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def process_payment(data: dict) -> dict:
        """Process payment status update.
        
        Args:
            data: Payment webhook data
            
        Returns:
            dict: Processing result
        """
        order_id = data.get('order_id')
        order_status = data.get('order_status')
        payment_id = data.get('payment_id')
        order_amount = data.get('order_amount')
        
        logger.info(f"Processing payment: {order_id} Status: {order_status}")
        
        if order_status == 'approved':
            # Payment successful
            return {
                'status': 'success',
                'message': 'Payment processed successfully',
                'order_id': order_id,
                'payment_id': payment_id,
                'timestamp': datetime.now().isoformat()
            }
        elif order_status == 'declined':
            # Payment failed
            return {
                'status': 'failed',
                'message': 'Payment declined',
                'order_id': order_id,
                'timestamp': datetime.now().isoformat()
            }
        elif order_status == 'expired':
            # Payment expired
            return {
                'status': 'expired',
                'message': 'Payment expired',
                'order_id': order_id,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'pending',
                'message': f'Payment status: {order_status}',
                'order_id': order_id,
                'timestamp': datetime.now().isoformat()
            }


@app.post('/webhook/fondy')
async def handle_fondy_webhook(request: Request):
    """Handle Fondy payment webhook.
    
    Endpoint: POST /webhook/fondy
    
    Fondy sends payment status updates via POST request with:
    - merchant_id
    - order_id
    - order_status (approved, declined, expired, etc.)
    - payment_id
    - order_amount
    - order_currency
    - response_signature_string
    
    Returns:
        JSONResponse with webhook processing result
    """
    try:
        # Parse webhook payload
        body = await request.json()
        logger.info(f"Received Fondy webhook: {body.get('order_id')}")
        
        # Verify signature
        signature = body.get('response_signature_string')
        if not signature:
            logger.error("Missing signature in webhook")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        if not FondyWebhookHandler.verify_signature(body, signature):
            logger.error(f"Invalid signature for order {body.get('order_id')}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Process payment
        result = FondyWebhookHandler.process_payment(body)
        
        # Log successful processing
        logger.info(f"Webhook processed: {result['order_id']} - {result['status']}")
        
        return JSONResponse(
            status_code=200,
            content={
                'status': 'ok',
                'result': result
            }
        )
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get('/health')
async def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'fondy-webhook-handler',
        'timestamp': datetime.now().isoformat()
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
