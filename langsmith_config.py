"""
LangSmith Integration for NexusAI
Provides tracing, token tracking, and cost analysis for all LLM operations.
"""

import os
import functools
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging

# LangSmith imports
from langsmith import Client, traceable
from langsmith.run_helpers import get_current_run_tree

logger = logging.getLogger(__name__)

# Initialize LangSmith Client
def init_langsmith():
    """
    Initialize LangSmith client with API key from environment.
    Set LANGSMITH_API_KEY in your .env file.
    For organization-scoped keys, also set LANGSMITH_WORKSPACE_ID.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    project_name = os.getenv("LANGSMITH_PROJECT", "NexusAI")
    workspace_id = os.getenv("LANGSMITH_WORKSPACE_ID")  # For org-scoped keys
    
    if not api_key:
        logger.warning("LANGSMITH_API_KEY not found. LangSmith tracing will be disabled.")
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return None
    
    # Enable tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project_name
    os.environ["LANGSMITH_API_KEY"] = api_key
    
    # Set workspace ID if provided (for org-scoped API keys)
    if workspace_id:
        os.environ["LANGSMITH_WORKSPACE_ID"] = workspace_id
    
    # Initialize client with workspace_id if provided
    try:
        if workspace_id:
            client = Client(api_key=api_key, api_url="https://api.smith.langchain.com")
            # The workspace_id is automatically picked up from the environment variable
            logger.info(f"LangSmith initialized with workspace ID. Project: {project_name}")
        else:
            client = Client(api_key=api_key)
            logger.info(f"LangSmith initialized. Project: {project_name}")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LangSmith client: {e}")
        return None

# Global client instance
langsmith_client = init_langsmith()

# Pricing information (as of 2024 - update as needed)
# Prices are per 1M tokens
PRICING = {
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-flash-image": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},  # Free tier
    "gemini-2.0-flash-thinking-exp-1219": {"input": 0.0, "output": 0.0},  # Free tier
    "gemini-3-pro-preview": {"input": 1.25, "output": 5.00},
    "gemini-pro": {"input": 0.50, "output": 1.50},
    "veo-001": {"input": 0.0, "output": 0.0},  # Video generation - pricing TBD
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of an LLM call based on token usage.
    
    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Cost in USD
    """
    if model not in PRICING:
        logger.warning(f"Pricing not available for model: {model}")
        return 0.0
    
    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    return input_cost + output_cost


def trace_llm_call(
    name: str,
    service: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace LLM calls with LangSmith.
    
    Args:
        name: Name of the operation (e.g., "generate_image", "chat")
        service: Service name (e.g., "ImageGeneration", "Chat")
        metadata: Additional metadata to attach to the trace
    
    Usage:
        @trace_llm_call(name="generate_image", service="ImageGeneration")
        def my_function(prompt: str, model: str):
            # Your LLM call here
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        @traceable(
            name=name,
            run_type="llm",
            project_name=os.getenv("LANGSMITH_PROJECT", "NexusAI"),
            metadata={
                "service": service,
                **(metadata or {})
            }
        )
        def wrapper(*args, **kwargs):
            if not langsmith_client:
                # LangSmith disabled, just run the function
                return func(*args, **kwargs)
            
            start_time = datetime.now()
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Try to extract token usage and cost if available
                if isinstance(result, tuple) and len(result) >= 5:
                    # Assuming format: (data, mime, error, status, tokens)
                    tokens = result[4] if len(result) > 4 else 0
                    model = kwargs.get("model", "unknown")
                    
                    # Get current run to add metadata
                    run_tree = get_current_run_tree()
                    if run_tree:
                        # Estimate input/output split (rough approximation)
                        input_tokens = int(tokens * 0.3)  # ~30% input
                        output_tokens = int(tokens * 0.7)  # ~70% output
                        
                        cost = calculate_cost(model, input_tokens, output_tokens)
                        
                        run_tree.metadata.update({
                            "total_tokens": tokens,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "estimated_cost_usd": cost,
                            "model": model,
                            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
                        })
                
                return result
                
            except Exception as e:
                # Log the error in LangSmith
                run_tree = get_current_run_tree()
                if run_tree:
                    run_tree.metadata.update({
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                raise
        
        return wrapper
    return decorator


def trace_async_llm_call(
    name: str,
    service: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Async version of trace_llm_call decorator.
    
    Args:
        name: Name of the operation
        service: Service name
        metadata: Additional metadata
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        @traceable(
            name=name,
            run_type="llm",
            project_name=os.getenv("LANGSMITH_PROJECT", "NexusAI"),
            metadata={
                "service": service,
                **(metadata or {})
            }
        )
        async def wrapper(*args, **kwargs):
            if not langsmith_client:
                return await func(*args, **kwargs)
            
            start_time = datetime.now()
            
            try:
                result = await func(*args, **kwargs)
                
                # Add metadata to run
                run_tree = get_current_run_tree()
                if run_tree:
                    run_tree.metadata.update({
                        "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
                    })
                
                return result
                
            except Exception as e:
                run_tree = get_current_run_tree()
                if run_tree:
                    run_tree.metadata.update({
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                raise
        
        return wrapper
    return decorator


class TokenTracker:
    """
    Track token usage and costs across all services.
    """
    def __init__(self):
        self.usage_data = []
    
    def log_usage(
        self,
        service: str,
        operation: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None
    ):
        """
        Log token usage for an operation.
        """
        total_tokens = input_tokens + output_tokens
        cost = calculate_cost(model, input_tokens, output_tokens)
        
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "user_id": user_id,
            "job_id": job_id
        }
        
        self.usage_data.append(usage_entry)
        
        # Also send to LangSmith if available
        if langsmith_client:
            try:
                langsmith_client.create_feedback(
                    run_id=job_id or "unknown",
                    key="token_usage",
                    score=total_tokens,
                    value={
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost_usd": cost
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send feedback to LangSmith: {e}")
        
        return usage_entry
    
    def get_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage summary, optionally filtered by user.
        """
        filtered_data = self.usage_data
        if user_id:
            filtered_data = [d for d in self.usage_data if d.get("user_id") == user_id]
        
        if not filtered_data:
            return {
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "operations_count": 0
            }
        
        total_tokens = sum(d["total_tokens"] for d in filtered_data)
        total_cost = sum(d["cost_usd"] for d in filtered_data)
        
        # Group by service
        by_service = {}
        for entry in filtered_data:
            service = entry["service"]
            if service not in by_service:
                by_service[service] = {
                    "tokens": 0,
                    "cost": 0.0,
                    "count": 0
                }
            by_service[service]["tokens"] += entry["total_tokens"]
            by_service[service]["cost"] += entry["cost_usd"]
            by_service[service]["count"] += 1
        
        return {
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "operations_count": len(filtered_data),
            "by_service": by_service
        }


# Global token tracker
token_tracker = TokenTracker()


def get_langsmith_url(run_id: str) -> str:
    """
    Generate LangSmith dashboard URL for a specific run.
    
    Args:
        run_id: The run ID from LangSmith
    
    Returns:
        URL to view the trace in LangSmith
    """
    project_name = os.getenv("LANGSMITH_PROJECT", "NexusAI")
    return f"https://smith.langchain.com/o/default/projects/p/{project_name}/r/{run_id}"


# Export main utilities
__all__ = [
    "init_langsmith",
    "trace_llm_call",
    "trace_async_llm_call",
    "calculate_cost",
    "token_tracker",
    "TokenTracker",
    "get_langsmith_url",
    "langsmith_client"
]
