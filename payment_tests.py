import pytest
import json
from unittest.mock import patch, MagicMock
from payment_processor import process_payment, verify_payment
from webhook_handler import handle_fondy_webhook


class TestPaymentProcessing:
    """Test suite for payment processing"""

    def test_process_payment_success(self):
        """Test successful payment processing"""
        payment_data = {
            "amount": 5000,
            "currency": "USD",
            "customer_id": "cust_123",
            "description": "Monthly subscription"
        }
        
        with patch('payment_processor.fondy_client') as mock_fondy:
            mock_fondy.charge.return_value = {
                "status": "success",
                "transaction_id": "txn_abc123"
            }
            
            result = process_payment(payment_data)
            assert result["status"] == "success"
            assert result["transaction_id"] == "txn_abc123"

    def test_process_payment_insufficient_funds(self):
        """Test payment with insufficient funds"""
        payment_data = {
            "amount": 50000,
            "currency": "USD",
            "customer_id": "cust_456"
        }
        
        with patch('payment_processor.fondy_client') as mock_fondy:
            mock_fondy.charge.return_value = {
                "status": "declined",
                "error_code": "insufficient_funds"
            }
            
            result = process_payment(payment_data)
            assert result["status"] == "declined"

    def test_verify_payment(self):
        """Test payment verification"""
        transaction_id = "txn_abc123"
        
        with patch('payment_processor.fondy_client') as mock_fondy:
            mock_fondy.verify_transaction.return_value = {
                "status": "completed",
                "amount": 5000
            }
            
            result = verify_payment(transaction_id)
            assert result["status"] == "completed"

    def test_webhook_signature_validation(self):
        """Test webhook signature validation"""
        webhook_data = {
            "order_id": "order_123",
            "amount": 5000,
            "signature": "valid_signature"
        }
        
        with patch('webhook_handler.validate_signature') as mock_validate:
            mock_validate.return_value = True
            result = handle_fondy_webhook(webhook_data)
            mock_validate.assert_called_once()

    def test_payment_idempotency(self):
        """Test idempotent payment processing"""
        payment_data = {
            "amount": 5000,
            "idempotency_key": "key_123"
        }
        
        with patch('payment_processor.cache') as mock_cache:
            mock_cache.get.return_value = {
                "status": "success",
                "transaction_id": "txn_cached"
            }
            
            result = process_payment(payment_data)
            assert result["transaction_id"] == "txn_cached"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
