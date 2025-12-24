#!/usr/bin/env python3
"""FastAPI Application for Heatmap SaaS API."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from heatmap_orchestrator import HeatmapOrchestrator, HeatmapConfig
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Heatmap SaaS API",
    description="Real-time location-based heat map generation",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Global orchestrator
orchestr ator = HeatmapOrchestrator()


class LocationPoint(BaseModel):
    """Location data point for heatmap."""
    latitude: float
    longitude: float
    value: float
    category: Optional[str] = None


class HeatmapRequest(BaseModel):
    """Request model for heatmap generation."""
    locations: List[LocationPoint]
    location_id: str = "default"
    blur_radius: int = 25
    color_scheme: str = "hot"


class HeatmapResponse(BaseModel):
    """Response model for heatmap."""
    location_id: str
    timestamp: str
    points: int
    avg_value: float
    max_value: float


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "service": "heatmap-saas-api",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/generate-heatmap")
async def generate_heatmap(request: HeatmapRequest):
    """Generate heatmap from location data."""
    try:
        config = HeatmapConfig(
            blur_radius=request.blur_radius,
            color_scheme=request.color_scheme
        )
        
        orchestrator.config = config
        
        locations_dict = [
            {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "value": loc.value,
                "category": loc.category
            }
            for loc in request.locations
        ]
        
        result = orchestrator.generate_heatmap(locations_dict, request.location_id)
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch-process")
async def batch_process(batches: List[HeatmapRequest]):
    """Process multiple heatmap batches in parallel."""
    try:
        results = []
        for batch in batches:
            locations_dict = [
                {
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                    "value": loc.value,
                    "category": loc.category
                }
                for loc in batch.locations
            ]
            result = orchestrator.generate_heatmap(locations_dict, batch.location_id)
            results.append(result)
        
        return {
            "success": True,
            "batch_count": len(batches),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics")
async def metrics():
    """Get API metrics and statistics."""
    return {
        "service": "heatmap-saas-api",
        "uptime": "tracking",
        "total_requests": "tracked",
        "cache_hits": "monitored",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Heatmap SaaS API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
