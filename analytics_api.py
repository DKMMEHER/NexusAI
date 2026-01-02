"""
Analytics API for LangSmith Integration
Provides endpoints to view token usage, costs, and LangSmith traces.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from auth import verify_token
from langsmith_config import token_tracker, langsmith_client, get_langsmith_url
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class TokenUsageResponse(BaseModel):
    """Response model for token usage data"""
    total_tokens: int
    total_cost_usd: float
    operations_count: int
    by_service: dict


class UsageEntry(BaseModel):
    """Individual usage entry"""
    timestamp: str
    service: str
    operation: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    user_id: Optional[str] = None
    job_id: Optional[str] = None


@router.get("/token-usage", response_model=TokenUsageResponse)
async def get_token_usage(
    user_id: str = Query(..., description="User ID to filter usage"),
    token_uid: str = Depends(verify_token)
):
    """
    Get token usage summary for a user.
    
    Returns:
        - Total tokens used
        - Total cost in USD
        - Number of operations
        - Breakdown by service
    """
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    summary = token_tracker.get_summary(user_id=user_id)
    return summary


@router.get("/usage-history", response_model=List[UsageEntry])
async def get_usage_history(
    user_id: str = Query(..., description="User ID to filter usage"),
    limit: int = Query(100, description="Maximum number of entries to return"),
    token_uid: str = Depends(verify_token)
):
    """
    Get detailed usage history for a user.
    
    Returns list of all operations with token usage and costs.
    """
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Filter by user_id
    user_usage = [
        entry for entry in token_tracker.usage_data
        if entry.get("user_id") == user_id
    ]
    
    # Sort by timestamp (newest first)
    user_usage.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Limit results
    return user_usage[:limit]


@router.get("/cost-breakdown")
async def get_cost_breakdown(
    user_id: str = Query(..., description="User ID to filter usage"),
    days: int = Query(7, description="Number of days to analyze"),
    token_uid: str = Depends(verify_token)
):
    """
    Get cost breakdown by service and model for the last N days.
    """
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter usage data
    filtered_usage = [
        entry for entry in token_tracker.usage_data
        if entry.get("user_id") == user_id
        and datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
    ]
    
    # Breakdown by service
    by_service = {}
    by_model = {}
    daily_costs = {}
    
    for entry in filtered_usage:
        service = entry["service"]
        model = entry["model"]
        date = entry["timestamp"][:10]  # YYYY-MM-DD
        cost = entry["cost_usd"]
        tokens = entry["total_tokens"]
        
        # By service
        if service not in by_service:
            by_service[service] = {"cost": 0.0, "tokens": 0, "operations": 0}
        by_service[service]["cost"] += cost
        by_service[service]["tokens"] += tokens
        by_service[service]["operations"] += 1
        
        # By model
        if model not in by_model:
            by_model[model] = {"cost": 0.0, "tokens": 0, "operations": 0}
        by_model[model]["cost"] += cost
        by_model[model]["tokens"] += tokens
        by_model[model]["operations"] += 1
        
        # Daily costs
        if date not in daily_costs:
            daily_costs[date] = 0.0
        daily_costs[date] += cost
    
    # Round costs
    for service in by_service.values():
        service["cost"] = round(service["cost"], 4)
    for model in by_model.values():
        model["cost"] = round(model["cost"], 4)
    daily_costs = {k: round(v, 4) for k, v in daily_costs.items()}
    
    return {
        "period_days": days,
        "total_cost_usd": round(sum(daily_costs.values()), 4),
        "total_tokens": sum(s["tokens"] for s in by_service.values()),
        "total_operations": sum(s["operations"] for s in by_service.values()),
        "by_service": by_service,
        "by_model": by_model,
        "daily_costs": daily_costs
    }


@router.get("/langsmith-traces")
async def get_langsmith_traces(
    user_id: str = Query(..., description="User ID to filter traces"),
    limit: int = Query(20, description="Number of traces to return"),
    token_uid: str = Depends(verify_token)
):
    """
    Get recent LangSmith trace URLs for a user.
    
    This allows users to view detailed waterfall traces in LangSmith.
    """
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    if not langsmith_client:
        return {
            "enabled": False,
            "message": "LangSmith is not configured. Set LANGSMITH_API_KEY in .env"
        }
    
    try:
        # Get recent runs from LangSmith
        # Filter by user_id in metadata
        runs = langsmith_client.list_runs(
            project_name="NexusAI",
            limit=limit,
            filter=f'eq(metadata.user_id, "{user_id}")'
        )
        
        traces = []
        for run in runs:
            traces.append({
                "run_id": str(run.id),
                "name": run.name,
                "run_type": run.run_type,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
                "status": run.status,
                "trace_url": get_langsmith_url(str(run.id)),
                "metadata": run.extra.get("metadata", {}) if run.extra else {}
            })
        
        return {
            "enabled": True,
            "traces": traces,
            "count": len(traces)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch LangSmith traces: {e}")
        return {
            "enabled": True,
            "error": str(e),
            "traces": []
        }


@router.get("/model-performance")
async def get_model_performance(
    user_id: str = Query(..., description="User ID to filter usage"),
    token_uid: str = Depends(verify_token)
):
    """
    Get performance metrics for each model used.
    
    Returns:
        - Average tokens per request
        - Average cost per request
        - Total usage per model
    """
    if token_uid != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Filter by user
    user_usage = [
        entry for entry in token_tracker.usage_data
        if entry.get("user_id") == user_id
    ]
    
    # Group by model
    model_stats = {}
    for entry in user_usage:
        model = entry["model"]
        if model not in model_stats:
            model_stats[model] = {
                "total_tokens": 0,
                "total_cost": 0.0,
                "request_count": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        
        model_stats[model]["total_tokens"] += entry["total_tokens"]
        model_stats[model]["total_cost"] += entry["cost_usd"]
        model_stats[model]["request_count"] += 1
        model_stats[model]["input_tokens"] += entry["input_tokens"]
        model_stats[model]["output_tokens"] += entry["output_tokens"]
    
    # Calculate averages
    for model, stats in model_stats.items():
        count = stats["request_count"]
        if count > 0:
            stats["avg_tokens_per_request"] = round(stats["total_tokens"] / count, 2)
            stats["avg_cost_per_request"] = round(stats["total_cost"] / count, 4)
            stats["avg_input_tokens"] = round(stats["input_tokens"] / count, 2)
            stats["avg_output_tokens"] = round(stats["output_tokens"] / count, 2)
        
        stats["total_cost"] = round(stats["total_cost"], 4)
    
    return {
        "models": model_stats,
        "total_models_used": len(model_stats)
    }


@router.get("/health")
async def analytics_health():
    """Health check for analytics service"""
    return {
        "status": "healthy",
        "langsmith_enabled": langsmith_client is not None,
        "total_tracked_operations": len(token_tracker.usage_data)
    }


# Export router
__all__ = ["router"]
