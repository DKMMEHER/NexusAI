# LangSmith Integration Guide for NexusAI

## Overview

This guide explains how to use LangSmith for **tracing**, **token tracking**, and **cost analysis** in your NexusAI project.

## What is LangSmith?

LangSmith is an observability platform for LLM applications that provides:
- **Trace Waterfall Visualization**: See the complete flow of your LLM calls
- **Token Usage Tracking**: Monitor input/output tokens for each operation
- **Cost Analysis**: Calculate costs based on model pricing
- **Performance Monitoring**: Track latency and errors
- **Debugging**: Inspect inputs, outputs, and intermediate steps

## Setup

### 1. Get LangSmith API Key

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Sign up or log in
3. Navigate to **Settings** → **API Keys**
4. Create a new API key
5. Copy the key

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=NexusAI
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langsmith` - LangSmith SDK
- `langchain` - LangChain core (required by langsmith)

## Usage

### Basic Tracing

#### 1. Import the Tracing Utilities

```python
from langsmith_config import trace_llm_call, trace_async_llm_call, token_tracker
```

#### 2. Decorate Your LLM Functions

**For synchronous functions:**

```python
@trace_llm_call(
    name="generate_image",
    service="ImageGeneration",
    metadata={"feature": "text-to-image"}
)
def call_gemini_api(prompt: str, model: str, api_key: str):
    # Your LLM call here
    response = requests.post(...)
    return response
```

**For async functions:**

```python
@trace_async_llm_call(
    name="generate_script",
    service="Director",
    metadata={"feature": "script-generation"}
)
async def generate_script(topic: str, duration: int):
    # Your async LLM call here
    response = await model.generate_content_async(...)
    return response
```

### Advanced Tracing - Hierarchical Traces

Create parent-child relationships to see the complete flow:

```python
from langsmith import traceable

@traceable(name="generate_video_workflow", run_type="chain")
async def generate_video(topic: str):
    # This is the parent trace
    
    # Step 1: Generate script (child trace)
    script = await generate_script_traced(topic)
    
    # Step 2: Generate scenes (child trace)
    scenes = await generate_scenes_traced(script)
    
    # Step 3: Stitch video (child trace)
    video = await stitch_video_traced(scenes)
    
    return video
```

This creates a **waterfall visualization** in LangSmith showing:
```
generate_video_workflow (1200ms)
├── generate_script_traced (500ms)
├── generate_scenes_traced (600ms)
└── stitch_video_traced (100ms)
```

### Token Tracking

Track token usage and costs:

```python
from langsmith_config import token_tracker

# Log token usage
token_tracker.log_usage(
    service="Chat",
    operation="chat_message",
    model="gemini-2.0-flash-exp",
    input_tokens=150,
    output_tokens=300,
    user_id="user123",
    job_id="job456"
)

# Get usage summary
summary = token_tracker.get_summary(user_id="user123")
print(f"Total tokens: {summary['total_tokens']}")
print(f"Total cost: ${summary['total_cost_usd']}")
print(f"By service: {summary['by_service']}")
```

### Adding Metadata to Traces

Add custom metadata to your traces for better filtering and analysis:

```python
from langsmith.run_helpers import get_current_run_tree

@trace_llm_call(name="generate_image", service="ImageGeneration")
def generate_image(prompt: str, model: str, user_id: str):
    # Get the current trace
    run_tree = get_current_run_tree()
    
    if run_tree:
        # Add custom metadata
        run_tree.metadata.update({
            "user_id": user_id,
            "prompt_length": len(prompt),
            "model": model,
            "feature": "image_generation"
        })
        
        # Set inputs (visible in LangSmith UI)
        run_tree.inputs = {
            "prompt": prompt,
            "model": model
        }
    
    # Your LLM call
    result = call_api(prompt, model)
    
    if run_tree:
        # Set outputs (visible in LangSmith UI)
        run_tree.outputs = {
            "success": True,
            "image_size": len(result)
        }
    
    return result
```

## Integration Examples

### Example 1: ImageGeneration Service

See `ImageGeneration/langsmith_integration_example.py` for a complete example.

Key points:
- Wrap the Gemini API call with `@trace_llm_call`
- Log token usage with `token_tracker.log_usage()`
- Add metadata for filtering (user_id, job_id, etc.)

### Example 2: Chat Service

```python
from langsmith_config import trace_async_llm_call, token_tracker
import google.generativeai as genai

@trace_async_llm_call(
    name="chat_completion",
    service="Chat",
    metadata={"feature": "conversational_ai"}
)
async def chat_with_gemini(message: str, model: str, user_id: str):
    gen_model = genai.GenerativeModel(model_name=model)
    response = await gen_model.generate_content_async(message)
    
    # Track tokens
    if response.usage_metadata:
        token_tracker.log_usage(
            service="Chat",
            operation="chat",
            model=model,
            input_tokens=response.usage_metadata.prompt_token_count,
            output_tokens=response.usage_metadata.candidates_token_count,
            user_id=user_id
        )
    
    return response.text
```

### Example 3: Director Service (Complex Workflow)

```python
from langsmith import traceable
from langsmith_config import trace_async_llm_call

@traceable(name="create_movie", run_type="chain", project_name="NexusAI")
async def create_movie(topic: str, duration: int):
    """
    Top-level trace for the entire movie creation workflow.
    This will show all sub-steps in a waterfall.
    """
    # Step 1: Generate script
    script = await generate_script_traced(topic, duration)
    
    # Step 2: Generate scenes
    scenes = []
    for scene in script:
        video = await generate_scene_traced(scene)
        scenes.append(video)
    
    # Step 3: Stitch final video
    final_video = await stitch_video_traced(scenes)
    
    return final_video

@trace_async_llm_call(name="generate_script", service="Director")
async def generate_script_traced(topic: str, duration: int):
    # Your script generation logic
    pass

@trace_async_llm_call(name="generate_scene", service="VideoGeneration")
async def generate_scene_traced(scene_prompt: str):
    # Your scene generation logic
    pass
```

## Analytics API

Use the analytics API to view usage data:

### Get Token Usage Summary

```bash
GET /analytics/token-usage?user_id=user123
```

Response:
```json
{
  "total_tokens": 15000,
  "total_cost_usd": 0.0225,
  "operations_count": 10,
  "by_service": {
    "ImageGeneration": {
      "tokens": 8000,
      "cost": 0.012,
      "count": 5
    },
    "Chat": {
      "tokens": 7000,
      "cost": 0.0105,
      "count": 5
    }
  }
}
```

### Get Usage History

```bash
GET /analytics/usage-history?user_id=user123&limit=50
```

### Get Cost Breakdown

```bash
GET /analytics/cost-breakdown?user_id=user123&days=7
```

Response:
```json
{
  "period_days": 7,
  "total_cost_usd": 0.0225,
  "total_tokens": 15000,
  "total_operations": 10,
  "by_service": {...},
  "by_model": {
    "gemini-2.5-flash": {
      "cost": 0.015,
      "tokens": 10000,
      "operations": 7
    }
  },
  "daily_costs": {
    "2026-01-01": 0.010,
    "2026-01-02": 0.0125
  }
}
```

### Get LangSmith Traces

```bash
GET /analytics/langsmith-traces?user_id=user123&limit=20
```

Response:
```json
{
  "enabled": true,
  "traces": [
    {
      "run_id": "abc123",
      "name": "generate_image",
      "run_type": "llm",
      "start_time": "2026-01-02T10:00:00",
      "end_time": "2026-01-02T10:00:05",
      "status": "success",
      "trace_url": "https://smith.langchain.com/o/default/projects/p/NexusAI/r/abc123",
      "metadata": {
        "user_id": "user123",
        "model": "gemini-2.5-flash",
        "total_tokens": 500
      }
    }
  ],
  "count": 1
}
```

## Viewing Traces in LangSmith

### 1. Access LangSmith Dashboard

Go to [https://smith.langchain.com/](https://smith.langchain.com/)

### 2. Select Your Project

Navigate to **Projects** → **NexusAI**

### 3. View Traces

You'll see a list of all traces with:
- **Name**: Operation name (e.g., "generate_image")
- **Status**: Success/Error
- **Duration**: How long it took
- **Tokens**: Token usage
- **Cost**: Estimated cost

### 4. Click on a Trace

This opens the **Waterfall View** showing:
- **Timeline**: Visual representation of execution flow
- **Inputs**: What was sent to the LLM
- **Outputs**: What the LLM returned
- **Metadata**: Custom metadata (user_id, model, etc.)
- **Token Usage**: Input/output token breakdown
- **Cost**: Calculated cost

### 5. Filter and Search

Use filters to find specific traces:
- Filter by user_id: `metadata.user_id = "user123"`
- Filter by model: `metadata.model = "gemini-2.5-flash"`
- Filter by status: `status = "error"`
- Search by prompt text

## Cost Calculation

Costs are calculated based on the pricing in `langsmith_config.py`:

```python
PRICING = {
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # per 1M tokens
    "gemini-3-pro-preview": {"input": 1.25, "output": 5.00},
    # ... more models
}
```

**Update these prices** as Google updates their pricing.

Formula:
```
cost = (input_tokens / 1,000,000) * input_price + (output_tokens / 1,000,000) * output_price
```

## Best Practices

### 1. Always Add User Context

```python
run_tree.metadata.update({
    "user_id": user_id,
    "job_id": job_id,
    "session_id": session_id
})
```

This allows filtering traces by user in LangSmith.

### 2. Use Hierarchical Tracing

Create parent-child relationships for complex workflows:
- Parent: `create_movie`
- Children: `generate_script`, `generate_scenes`, `stitch_video`

### 3. Log Errors

```python
try:
    result = call_api()
except Exception as e:
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.error = str(e)
        run_tree.metadata["error_type"] = type(e).__name__
    raise
```

### 4. Add Meaningful Names

Use descriptive names for traces:
- ✅ `generate_image_with_grounding`
- ❌ `api_call`

### 5. Track Token Usage

Always log token usage for cost analysis:
```python
token_tracker.log_usage(
    service="YourService",
    operation="operation_name",
    model=model,
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    user_id=user_id
)
```

## Troubleshooting

### LangSmith Not Working

1. Check if `LANGSMITH_API_KEY` is set:
   ```python
   import os
   print(os.getenv("LANGSMITH_API_KEY"))
   ```

2. Check if tracing is enabled:
   ```python
   print(os.getenv("LANGCHAIN_TRACING_V2"))  # Should be "true"
   ```

3. Check logs for errors:
   ```
   logger.info("LangSmith initialized")
   ```

### Traces Not Appearing

1. Make sure you're using the `@traceable` or `@trace_llm_call` decorators
2. Check that the function is actually being called
3. Wait a few seconds - traces may take time to appear in the UI

### Cost Calculation Incorrect

1. Update pricing in `langsmith_config.py`
2. Verify token counts are being extracted correctly
3. Check if you're using the correct model name

## Next Steps

1. **Add Analytics to Frontend**: Create a dashboard showing token usage and costs
2. **Set Up Alerts**: Use LangSmith to alert on high costs or errors
3. **A/B Testing**: Compare different prompts or models using LangSmith
4. **Performance Optimization**: Identify slow operations in the waterfall view

## Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Python SDK](https://github.com/langchain-ai/langsmith-sdk)
- [Google Gemini Pricing](https://ai.google.dev/pricing)

---

**Questions?** Check the LangSmith docs or reach out to the team!
