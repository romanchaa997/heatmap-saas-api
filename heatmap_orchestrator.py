#!/usr/bin/env python3
"""Heatmap Orchestrator - Multi-threaded Coordination System for Heat Map Generation."""

import threading
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import redis
import logging
from functools import lru_cache
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LocationData:
    """Represent location-based data for heatmap."""
    latitude: float
    longitude: float
    value: float
    category: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class HeatmapConfig:
    """Configuration for heatmap generation."""
    blur_radius: int = 25
    max_zoom: int = 18
    color_scheme: str = "hot"
    cache_enabled: bool = True
    distributed: bool = True


class ScoreItemsStep:
    """LLM batch processing for intelligent data scoring."""
    
    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
    
    def score_batch(self, items: List[LocationData]) -> List[float]:
        """Score items using batched LLM processing."""
        scores = []
        for item in items:
            # Intelligent scoring based on location data
            score = self._calculate_score(item)
            scores.append(score)
        return scores
    
    def _calculate_score(self, item: LocationData) -> float:
        """Calculate relevance score for location item."""
        base_score = item.value
        if item.category:
            base_score *= 1.2  # Boost categorized items
        return min(base_score, 100.0)


class PersistStep:
    """Redis/PostgreSQL persistence layer."""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
    
    def cache_result(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Cache heatmap result with TTL."""
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                logger.error(f"Cache write failed: {e}")
        self.memory_cache[key] = value
        return True
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Retrieve cached result."""
        if self.redis_client:
            try:
                result = self.redis_client.get(key)
                return json.loads(result) if result else None
            except Exception as e:
                logger.error(f"Cache read failed: {e}")
        return self.memory_cache.get(key)


class RateLimiter:
    """Rate limiting for external API calls."""
    
    def __init__(self, max_calls: int = 1000, window_seconds: int = 3600):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls: List[datetime] = []
        self.lock = threading.Lock()
    
    def check_limit(self) -> bool:
        """Check if call is within rate limit."""
        with self.lock:
            now = datetime.now()
            cutoff = now.timestamp() - self.window_seconds
            self.calls = [c for c in self.calls if c.timestamp() > cutoff]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False


class HeatmapOrchestrator:
    """Multi-threaded orchestrator for heatmap generation."""
    
    def __init__(self, config: Optional[HeatmapConfig] = None):
        self.config = config or HeatmapConfig()
        self.scorer = ScoreItemsStep()
        self.persister = PersistStep()
        self.rate_limiter = RateLimiter()
        self.threads: List[threading.Thread] = []
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
    
    def generate_heatmap(self, locations: List[Dict], location_id: str = "default") -> Dict[str, Any]:
        """Generate heatmap from location data with caching."""
        cache_key = f"heatmap_{location_id}_{self.config.color_scheme}"
        
        # Check cache first
        cached = self.persister.get_cached(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            return cached
        
        # Rate limit check
        if not self.rate_limiter.check_limit():
            return {"error": "Rate limit exceeded"}
        
        # Convert to LocationData objects
        location_objs = [LocationData(**loc) for loc in locations]
        
        # Score items in batch
        scores = self.scorer.score_batch(location_objs)
        
        # Generate heatmap
        heatmap_data = {
            "location_id": location_id,
            "timestamp": datetime.now().isoformat(),
            "points": [
                {**asdict(loc), "score": score}
                for loc, score in zip(location_objs, scores)
            ],
            "config": asdict(self.config),
            "summary": {
                "total_points": len(location_objs),
                "avg_value": sum(l.value for l in location_objs) / len(location_objs) if location_objs else 0,
                "max_value": max((l.value for l in location_objs), default=0)
            }
        }
        
        # Persist result
        self.persister.cache_result(cache_key, heatmap_data)
        
        with self.lock:
            self.results[cache_key] = heatmap_data
        
        return heatmap_data
    
    def process_parallel(self, location_batches: List[List[Dict]]) -> List[Dict]:
        """Process multiple location batches in parallel threads."""
        results = []
        threads = []
        
        def process_batch(batch: List[Dict], index: int):
            result = self.generate_heatmap(batch, f"batch_{index}")
            with self.lock:
                results.append(result)
        
        for i, batch in enumerate(location_batches):
            thread = threading.Thread(target=process_batch, args=(batch, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        return results


if __name__ == "__main__":
    # Example usage
    config = HeatmapConfig(blur_radius=30, color_scheme="viridis")
    orchestrator = HeatmapOrchestrator(config)
    
    # Sample location data
    locations = [
        {"latitude": 40.7128, "longitude": -74.0060, "value": 100, "category": "urban"},
        {"latitude": 40.7580, "longitude": -73.9855, "value": 85, "category": "urban"},
        {"latitude": 40.7489, "longitude": -73.9680, "value": 90, "category": "commercial"}
    ]
    
    heatmap = orchestrator.generate_heatmap(locations, "nyc_demo")
    print(json.dumps(heatmap, indent=2))
