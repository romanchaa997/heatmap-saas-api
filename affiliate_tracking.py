import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class CommissionTier(Enum):
    """Commission tier levels"""
    BRONZE = 0.10  # 10%
    SILVER = 0.15  # 15%
    GOLD = 0.20    # 20%
    PLATINUM = 0.25  # 25%


class AffiliateTracker:
    """Affiliate tracking and commission management system"""

    def __init__(self, db_connection):
        """Initialize affiliate tracker"""
        self.db = db_connection
        self.commission_tiers = CommissionTier
        self.cookie_duration = timedelta(days=30)  # 30-day cookie

    def generate_affiliate_code(self, affiliate_id: str) -> str:
        """Generate unique affiliate code"""
        unique_id = f"{affiliate_id}_{uuid.uuid4()}"
        code = hashlib.md5(unique_id.encode()).hexdigest()[:10].upper()
        return code

    def create_affiliate(self, name: str, email: str, tier: CommissionTier = CommissionTier.BRONZE) -> Dict:
        """Create new affiliate"""
        affiliate_id = str(uuid.uuid4())
        code = self.generate_affiliate_code(affiliate_id)
        
        affiliate_data = {
            "id": affiliate_id,
            "name": name,
            "email": email,
            "code": code,
            "tier": tier.name,
            "commission_rate": tier.value,
            "created_at": datetime.utcnow(),
            "status": "active",
            "total_referrals": 0,
            "total_commissions": 0.0
        }
        
        self.db.insert_affiliate(affiliate_data)
        return affiliate_data

    def track_click(self, affiliate_code: str, user_id: str, ip_address: str) -> Dict:
        """Track affiliate click"""
        click_id = str(uuid.uuid4())
        
        click_data = {
            "id": click_id,
            "affiliate_code": affiliate_code,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow(),
            "converted": False,
            "conversion_amount": 0.0
        }
        
        self.db.insert_click(click_data)
        return click_data

    def track_conversion(self, click_id: str, amount: float, customer_id: str) -> Dict:
        """Track affiliate conversion and calculate commission"""
        click = self.db.get_click(click_id)
        if not click:
            raise ValueError(f"Click ID {click_id} not found")
        
        affiliate_code = click['affiliate_code']
        affiliate = self.db.get_affiliate_by_code(affiliate_code)
        
        if not affiliate:
            raise ValueError(f"Affiliate {affiliate_code} not found")
        
        commission = amount * affiliate['commission_rate']
        
        conversion_data = {
            "click_id": click_id,
            "customer_id": customer_id,
            "amount": amount,
            "commission": commission,
            "affiliate_id": affiliate['id'],
            "timestamp": datetime.utcnow(),
            "status": "pending"
        }
        
        self.db.insert_conversion(conversion_data)
        self.db.update_click(click_id, {"converted": True, "conversion_amount": amount})
        
        return conversion_data

    def get_affiliate_stats(self, affiliate_id: str) -> Dict:
        """Get comprehensive affiliate statistics"""
        conversions = self.db.get_affiliate_conversions(affiliate_id)
        clicks = self.db.get_affiliate_clicks(affiliate_id)
        
        total_clicks = len(clicks)
        total_conversions = len([c for c in conversions if c['status'] == 'completed'])
        total_commission = sum([c['commission'] for c in conversions if c['status'] == 'completed'])
        
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        average_order_value = (sum([c['amount'] for c in conversions]) / total_conversions) if total_conversions > 0 else 0
        
        return {
            "affiliate_id": affiliate_id,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": conversion_rate,
            "total_revenue": sum([c['amount'] for c in conversions]),
            "total_commission": total_commission,
            "average_order_value": average_order_value,
            "pending_commission": sum([c['commission'] for c in conversions if c['status'] == 'pending']),
            "last_conversion": max([c['timestamp'] for c in conversions]) if conversions else None
        }

    def process_payout(self, affiliate_id: str, amount: float, method: str = "bank_transfer") -> Dict:
        """Process payout for affiliate"""
        payout_id = str(uuid.uuid4())
        
        payout_data = {
            "id": payout_id,
            "affiliate_id": affiliate_id,
            "amount": amount,
            "method": method,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "completed_at": None
        }
        
        self.db.insert_payout(payout_data)
        
        # Update affiliate commission tracking
        self.db.update_affiliate(affiliate_id, {
            "pending_payout": 0.0
        })
        
        return payout_data

    def upgrade_affiliate_tier(self, affiliate_id: str, new_tier: CommissionTier) -> Dict:
        """Upgrade affiliate to higher commission tier"""
        affiliate = self.db.get_affiliate(affiliate_id)
        
        old_rate = affiliate['commission_rate']
        new_rate = new_tier.value
        
        self.db.update_affiliate(affiliate_id, {
            "tier": new_tier.name,
            "commission_rate": new_rate
        })
        
        return {
            "affiliate_id": affiliate_id,
            "old_tier": affiliate['tier'],
            "new_tier": new_tier.name,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "upgraded_at": datetime.utcnow()
        }

    def get_top_affiliates(self, limit: int = 10, period_days: int = 30) -> List[Dict]:
        """Get top performing affiliates"""
        start_date = datetime.utcnow() - timedelta(days=period_days)
        return self.db.get_top_affiliates(start_date, limit)

    def get_affiliate_leaderboard(self) -> List[Dict]:
        """Get affiliate leaderboard"""
        affiliates = self.db.get_all_affiliates()
        
        leaderboard = []
        for affiliate in affiliates:
            stats = self.get_affiliate_stats(affiliate['id'])
            leaderboard.append({
                "rank": 0,  # Will be filled
                "name": affiliate['name'],
                "conversions": stats['total_conversions'],
                "commission": stats['total_commission'],
                "tier": affiliate['tier']
            })
        
        # Sort by commission
        leaderboard.sort(key=lambda x: x['commission'], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard, 1):
            entry['rank'] = i
        
        return leaderboard

    def generate_tracking_url(self, affiliate_code: str, landing_page: str = "/") -> str:
        """Generate tracking URL for affiliate"""
        return f"https://api.heatmap-saas.com{landing_page}?aff={affiliate_code}"

    def validate_affiliate_code(self, code: str) -> bool:
        """Validate affiliate code"""
        affiliate = self.db.get_affiliate_by_code(code)
        return affiliate is not None and affiliate['status'] == 'active'
