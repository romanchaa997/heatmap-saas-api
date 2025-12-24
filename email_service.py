ф"""SendGrid Email Service for Heatmap SaaS.

Handles:
- Transactional emails (order confirmations)
- Welcome emails
- Payment receipts
- Status updates
"""

from typing import Optional, List
import os
import logging
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@heatmap-saas-api.com')


class EmailService:
    """Manage email delivery via SendGrid."""
    
    def __init__(self):
        self.client = SendGridAPIClient(SENDGRID_API_KEY) if SENDGRID_API_KEY else None
    
    async def send_welcome_email(self, recipient_email: str, name: str, tier: str) -> bool:
        """Send welcome email to new customer."""
        try:
            subject = f"Welcome to Heatmap SaaS - {tier.title()} Plan"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Welcome to Heatmap SaaS!</h2>
                    <p>Hi {name},</p>
                    <p>Your account has been created successfully with the <strong>{tier.title()}</strong> plan.</p>
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Verify your email address</li>
                        <li>Visit your <a href="https://dashboard.heatmap-saas.com">dashboard</a></li>
                        <li>Generate API keys</li>
                        <li>Start integrating</li>
                    </ol>
                    <p><strong>API Documentation:</strong> <a href="https://docs.heatmap-saas.com">Read the docs</a></p>
                    <p>Support: support@heatmap-saas.com</p>
                </body>
            </html>
            """
            
            if not self.client:
                logger.warning(f"SendGrid not configured. Email not sent to {recipient_email}")
                return False
            
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = await asyncio.to_thread(self.client.send, message)
            logger.info(f"Welcome email sent to {recipient_email}. Status: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Error sending welcome email to {recipient_email}: {str(e)}")
            return False
    
    async def send_order_confirmation(self, recipient_email: str, order_id: str, amount: float, tier: str) -> bool:
        """Send order confirmation email."""
        try:
            subject = f"Order Confirmation - {order_id}"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Order Confirmed!</h2>
                    <p>Thank you for your order.</p>
                    <p><strong>Order Details:</strong></p>
                    <ul>
                        <li>Order ID: <code>{order_id}</code></li>
                        <li>Amount: <strong>${amount:.2f}</strong></li>
                        <li>Plan: <strong>{tier.title()}</strong></li>
                        <li>Status: <span style="color: green;">✓ Confirmed</span></li>
                    </ul>
                    <p>Your API access is now active. Visit your <a href="https://dashboard.heatmap-saas.com">dashboard</a> to get started.</p>
                </body>
            </html>
            """
            
            if not self.client:
                logger.warning(f"SendGrid not configured. Email not sent to {recipient_email}")
                return False
            
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = await asyncio.to_thread(self.client.send, message)
            logger.info(f"Order confirmation sent to {recipient_email}. Status: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Error sending order confirmation to {recipient_email}: {str(e)}")
            return False
    
    async def send_payment_receipt(self, recipient_email: str, transaction_id: str, amount: float, payment_method: str) -> bool:
        """Send payment receipt email."""
        try:
            subject = f"Payment Receipt - {transaction_id}"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Payment Receipt</h2>
                    <p><strong>Transaction ID:</strong> {transaction_id}</p>
                    <p><strong>Amount:</strong> ${amount:.2f} USD</p>
                    <p><strong>Payment Method:</strong> {payment_method.upper()}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="color: green;">✓ Payment Successful</p>
                </body>
            </html>
            """
            
            if not self.client:
                logger.warning(f"SendGrid not configured. Email not sent to {recipient_email}")
                return False
            
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = await asyncio.to_thread(self.client.send, message)
            logger.info(f"Receipt sent to {recipient_email}. Status: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Error sending receipt to {recipient_email}: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()


if __name__ == '__main__':
    print("SendGrid Email Service initialized")
    print(f"API Key configured: {bool(SENDGRID_API_KEY)}")
    print(f"From email: {FROM_EMAIL}")

from datetime import datetime
