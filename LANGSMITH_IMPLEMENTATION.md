# LangSmith Integration - Implementation Summary

## 🎯 What Has Been Implemented

This implementation provides **complete observability** for your NexusAI project with:

1. **LangSmith Tracing** - Waterfall visualization of all LLM calls
2. **Token Tracking** - Monitor input/output tokens for every operation
3. **Cost Analysis** - Calculate costs based on model pricing
4. **Analytics API** - REST endpoints for usage data
5. **Dashboard** - Beautiful UI to visualize analytics

---

## 📁 Files Created

### Core Integration

1. **`langsmith_config.py`** - Main integration module
   - `@trace_llm_call` - Decorator for synchronous LLM calls
   - `@trace_async_llm_call` - Decorator for async LLM calls
   - `TokenTracker` - Track token usage and costs
   - `calculate_cost()` - Calculate costs based on pricing
   - Automatic initialization of LangSmith client

2. **`analytics_api.py`** - Analytics REST API
   - `GET /analytics/token-usage` - Get token usage summary
   - `GET /analytics/usage-history` - Get detailed usage history
   - `GET /analytics/cost-breakdown` - Get cost breakdown by service/model
   - `GET /analytics/langsmith-traces` - Get LangSmith trace URLs
   - `GET /analytics/model-performance` - Get performance metrics per model

### Examples & Documentation

3. **`ImageGeneration/langsmith_integration_example.py`** - Integration example
   - Shows how to wrap Gemini API calls
   - Demonstrates hierarchical tracing
   - Example endpoint integration

4. **`LANGSMITH_GUIDE.md`** - Comprehensive guide
   - Setup instructions
   - Usage examples
   - Best practices
   - Troubleshooting

5. **`test_langsmith_setup.py`** - Verification script
   - Check environment variables
   - Test SDK installation
   - Test LangSmith connection
   - Test tracing functionality

### Frontend

6. **`frontend/analytics_dashboard.html`** - Analytics dashboard
   - Real-time token usage display
   - Cost analysis visualization
   - Service breakdown charts
   - LangSmith trace links

### Configuration

7. **`requirements.txt`** - Updated dependencies
   - Added `langsmith`
   - Added `langchain`

8. **`.env.example`** - Updated environment template
   - Added `LANGSMITH_API_KEY`
   - Added `LANGSMITH_PROJECT`

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get LangSmith API Key

1. Go to https://smith.langchain.com/
2. Sign up / Log in
3. Settings → API Keys → Create new key
4. Copy the key

### 3. Configure Environment

Add to your `.env` file:

```bash
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_PROJECT=NexusAI
```

### 4. Verify Setup

```bash
python test_langsmith_setup.py
```

This will check:
- ✅ Environment variables are set
- ✅ LangSmith SDK is installed
- ✅ Connection to LangSmith works
- ✅ Tracing functionality works
- ✅ Cost calculation works

---

## 💡 How to Use

### Basic Tracing

```python
from langsmith_config import trace_llm_call

@trace_llm_call(
    name="generate_image",
    service="ImageGeneration",
    metadata={"feature": "text-to-image"}
)
def call_gemini_api(prompt: str, model: str):
    # Your LLM call here
    response = requests.post(...)
    return response
```

### Async Tracing

```python
from langsmith_config import trace_async_llm_call

@trace_async_llm_call(
    name="generate_script",
    service="Director"
)
async def generate_script(topic: str):
    # Your async LLM call
    response = await model.generate_content_async(...)
    return response
```

### Hierarchical Tracing (Waterfall)

```python
from langsmith import traceable

@traceable(name="create_movie", run_type="chain")
async def create_movie(topic: str):
    # Parent trace
    script = await generate_script(topic)  # Child trace 1
    scenes = await generate_scenes(script)  # Child trace 2
    video = await stitch_video(scenes)      # Child trace 3
    return video
```

This creates a waterfall view in LangSmith:
```
create_movie (1200ms)
├── generate_script (500ms)
├── generate_scenes (600ms)
└── stitch_video (100ms)
```

### Token Tracking

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

# Get summary
summary = token_tracker.get_summary(user_id="user123")
print(f"Total cost: ${summary['total_cost_usd']}")
```

---

## 🔌 Integration into Your Services

### Example: ImageGeneration Service

```python
# In ImageGeneration/backend.py

from langsmith_config import trace_llm_call, token_tracker

@trace_llm_call(
    name="gemini_image_generation",
    service="ImageGeneration"
)
def call_nano_banana(api_key, prompt, model, user_id=None, job_id=None):
    # Your existing code
    response = requests.post(...)
    
    # Extract tokens
    usage = response.json().get('usageMetadata', {})
    input_tokens = usage.get('promptTokenCount', 0)
    output_tokens = usage.get('candidatesTokenCount', 0)
    
    # Track usage
    if user_id:
        token_tracker.log_usage(
            service="ImageGeneration",
            operation="generate_image",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            user_id=user_id,
            job_id=job_id
        )
    
    return result
```

### Example: Chat Service

```python
# In Chat/backend.py

from langsmith_config import trace_async_llm_call, token_tracker

@trace_async_llm_call(
    name="chat_completion",
    service="Chat"
)
async def chat_endpoint(message: str, model: str, user_id: str):
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

### Add Analytics API to Your Service

```python
# In any backend.py

from analytics_api import router as analytics_router

app = FastAPI()
app.include_router(analytics_router)
```

---

## 📊 Analytics API Endpoints

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
    "ImageGeneration": {"tokens": 8000, "cost": 0.012, "count": 5},
    "Chat": {"tokens": 7000, "cost": 0.0105, "count": 5}
  }
}
```

### Get Cost Breakdown

```bash
GET /analytics/cost-breakdown?user_id=user123&days=7
```

### Get LangSmith Traces

```bash
GET /analytics/langsmith-traces?user_id=user123&limit=20
```

Returns trace URLs that link directly to LangSmith dashboard.

---

## 🎨 Analytics Dashboard

Open `frontend/analytics_dashboard.html` in your browser to view:

- **Total Tokens** - All-time token usage
- **Total Cost** - Cumulative cost in USD
- **Operations Count** - Number of LLM calls
- **Service Breakdown** - Visual bar chart by service
- **Recent Traces** - Links to LangSmith waterfall views

**To use:**
1. Update `API_BASE` in the HTML file to your backend URL
2. Open in browser
3. Enter user ID
4. Click "Load Analytics"

---

## 🔍 Viewing Traces in LangSmith

### 1. Access Dashboard

Go to https://smith.langchain.com/

### 2. Select Project

Navigate to **Projects** → **NexusAI**

### 3. View Traces

Click on any trace to see:
- **Waterfall Timeline** - Visual execution flow
- **Inputs/Outputs** - What was sent/received
- **Token Usage** - Input/output token breakdown
- **Cost** - Calculated cost
- **Metadata** - Custom metadata (user_id, model, etc.)

### 4. Filter Traces

Use filters:
- `metadata.user_id = "user123"`
- `metadata.model = "gemini-2.5-flash"`
- `status = "error"`

---

## 💰 Cost Calculation

Costs are calculated based on pricing in `langsmith_config.py`:

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
cost = (input_tokens / 1,000,000) * input_price + 
       (output_tokens / 1,000,000) * output_price
```

---

## ✅ Best Practices

### 1. Always Add User Context

```python
from langsmith.run_helpers import get_current_run_tree

run_tree = get_current_run_tree()
if run_tree:
    run_tree.metadata.update({
        "user_id": user_id,
        "job_id": job_id
    })
```

### 2. Use Hierarchical Tracing

For complex workflows, create parent-child traces:
- Parent: `create_movie`
- Children: `generate_script`, `generate_scenes`, `stitch_video`

### 3. Track All Token Usage

Always log token usage for accurate cost analysis:
```python
token_tracker.log_usage(...)
```

### 4. Add Meaningful Names

Use descriptive names:
- ✅ `generate_image_with_grounding`
- ❌ `api_call`

### 5. Handle Errors Properly

```python
try:
    result = call_api()
except Exception as e:
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.error = str(e)
    raise
```

---

## 🐛 Troubleshooting

### LangSmith Not Working

1. Check environment variables:
   ```bash
   python -c "import os; print(os.getenv('LANGSMITH_API_KEY'))"
   ```

2. Run verification script:
   ```bash
   python test_langsmith_setup.py
   ```

### Traces Not Appearing

1. Verify you're using the decorators (`@trace_llm_call`)
2. Check that functions are being called
3. Wait a few seconds - traces may be delayed

### Cost Calculation Incorrect

1. Update pricing in `langsmith_config.py`
2. Verify token counts are extracted correctly
3. Check model name matches pricing dictionary

---

## 📚 Resources

- **LangSmith Documentation**: https://docs.smith.langchain.com/
- **LangSmith Dashboard**: https://smith.langchain.com/
- **Google Gemini Pricing**: https://ai.google.dev/pricing
- **Integration Guide**: See `LANGSMITH_GUIDE.md`
- **Example Code**: See `ImageGeneration/langsmith_integration_example.py`

---

## 🎯 Next Steps

1. **Get LangSmith API Key** - Sign up at https://smith.langchain.com/
2. **Configure .env** - Add `LANGSMITH_API_KEY`
3. **Run Verification** - `python test_langsmith_setup.py`
4. **Integrate Services** - Add tracing to your backend services
5. **View Traces** - Make some LLM calls and check LangSmith dashboard
6. **Monitor Costs** - Use analytics API to track spending

---

## 🤝 Support

For detailed instructions, see:
- `LANGSMITH_GUIDE.md` - Comprehensive guide
- `test_langsmith_setup.py` - Verification script
- `ImageGeneration/langsmith_integration_example.py` - Code examples

**Questions?** Check the LangSmith documentation or the integration guide!

---

**Happy Tracing! 🚀**
