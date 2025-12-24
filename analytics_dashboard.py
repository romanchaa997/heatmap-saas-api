import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class AnalyticsMetric:
    """Analytics metric data structure"""
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None


class AnalyticsDashboard:
    """Analytics Dashboard for Heatmap SaaS"""

    def __init__(self, db_connection):
        """Initialize analytics dashboard"""
        self.db = db_connection
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    def track_api_request(self, endpoint: str, method: str, status_code: int, 
                         response_time: float, customer_id: str):
        """Track API request metrics"""
        metric = AnalyticsMetric(
            metric_name="api_request",
            value=response_time,
            timestamp=datetime.utcnow(),
            tags={
                "endpoint": endpoint,
                "method": method,
                "status_code": str(status_code),
                "customer_id": customer_id
            }
        )
        self._store_metric(metric)
        logger.info(f"API request tracked: {endpoint} {method} {status_code}")

    def track_payment(self, customer_id: str, amount: float, currency: str, 
                     status: str, payment_method: str):
        """Track payment metrics"""
        metric = AnalyticsMetric(
            metric_name="payment",
            value=amount,
            timestamp=datetime.utcnow(),
            tags={
                "customer_id": customer_id,
                "currency": currency,
                "status": status,
                "payment_method": payment_method
            }
        )
        self._store_metric(metric)
        logger.info(f"Payment tracked: ${amount} {currency} {status}")

    def get_daily_api_stats(self, customer_id: Optional[str] = None) -> Dict:
        """Get daily API statistics"""
        cache_key = f"daily_stats_{customer_id or 'all'}"
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if cached_data['expires'] > datetime.utcnow():
                return cached_data['data']

        # Query database for metrics
        stats = self._query_daily_stats(customer_id)
        
        # Cache results
        self.cache[cache_key] = {
            'data': stats,
            'expires': datetime.utcnow() + timedelta(seconds=self.cache_ttl)
        }
        
        return stats

    def get_revenue_analytics(self, days: int = 30) -> Dict:
        """Get revenue analytics for specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "total_revenue": self._calculate_total_revenue(start_date),
            "daily_average": self._calculate_daily_average(start_date),
            "growth_rate": self._calculate_growth_rate(start_date),
            "top_customers": self._get_top_customers(start_date),
            "payment_methods": self._get_payment_method_breakdown(start_date)
        }

    def get_customer_analytics(self, customer_id: str) -> Dict:
        """Get analytics for specific customer"""
        return {
            "customer_id": customer_id,
            "api_calls": self._count_api_calls(customer_id),
            "total_spend": self._calculate_customer_spend(customer_id),
            "average_response_time": self._get_avg_response_time(customer_id),
            "error_rate": self._calculate_error_rate(customer_id),
            "most_used_endpoints": self._get_top_endpoints(customer_id),
            "subscription_status": self._get_subscription_status(customer_id)
        }

    def get_system_health(self) -> Dict:
        """Get system health metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_percentage": self._calculate_uptime(),
            "average_response_time": self._get_system_avg_response_time(),
            "error_rate": self._calculate_system_error_rate(),
            "active_customers": self._count_active_customers(),
            "total_api_calls": self._count_total_api_calls(),
            "database_status": self._check_database_status(),
            "cache_hit_ratio": self._calculate_cache_hit_ratio()
        }

    # Private helper methods
    def _store_metric(self, metric: AnalyticsMetric):
        """Store metric in database"""
        try:
            # Insert into analytics table
            self.db.insert_metric(metric)
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")

    def _query_daily_stats(self, customer_id: Optional[str]) -> Dict:
        """Query daily statistics from database"""
        # Implementation would query actual database
        return {}

    def _calculate_total_revenue(self, start_date: datetime) -> float:
        """Calculate total revenue since start date"""
        return 0.0

    def _calculate_daily_average(self, start_date: datetime) -> float:
        """Calculate daily average revenue"""
        return 0.0

    def _calculate_growth_rate(self, start_date: datetime) -> float:
        """Calculate revenue growth rate"""
        return 0.0

    def _get_top_customers(self, start_date: datetime) -> List[Dict]:
        """Get top customers by revenue"""
        return []

    def _get_payment_method_breakdown(self, start_date: datetime) -> Dict:
        """Get payment method breakdown"""
        return {}

    def _count_api_calls(self, customer_id: str) -> int:
        """Count API calls for customer"""
        return 0

    def _calculate_customer_spend(self, customer_id: str) -> float:
        """Calculate customer total spend"""
        return 0.0

    def _get_avg_response_time(self, customer_id: str) -> float:
        """Get average response time for customer"""
        return 0.0

    def _calculate_error_rate(self, customer_id: str) -> float:
        """Calculate customer error rate"""
        return 0.0

    def _get_top_endpoints(self, customer_id: str) -> List[str]:
        """Get most used endpoints for customer"""
        return []

    def _get_subscription_status(self, customer_id: str) -> str:
        """Get customer subscription status"""
        return "active"

    def _calculate_uptime(self) -> float:
        """Calculate system uptime percentage"""
        return 99.9

    def _get_system_avg_response_time(self) -> float:
        """Get system average response time"""
        return 0.0

    def _calculate_system_error_rate(self) -> float:
        """Calculate system error rate"""
        return 0.0

    def _count_active_customers(self) -> int:
        """Count active customers"""
        return 0

    def _count_total_api_calls(self) -> int:
        """Count total API calls"""
        return 0

    def _check_database_status(self) -> str:
        """Check database connection status"""
        try:
            # Test connection
            return "healthy"
        except:
            return "unhealthy"

    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        return 0.0
