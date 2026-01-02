# LangSmith Integration - Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add to .env
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=NexusAI

# 3. Verify setup
python test_langsmith_setup.py

# 4. Done! Start tracing your LLM calls
```

---

## 📝 Basic Usage

### Trace a Function

```python
from langsmith_config import trace_llm_call

@trace_llm_call(name="my_operation", service="MyService")
def my_function(prompt: str, model: str):
    # Your LLM call here
    response = call_api(prompt, model)
    return response
```

### Trace Async Function

```python
from langsmith_config import trace_async_llm_call

@trace_async_llm_call(name="my_async_op", service="MyService")
async def my_async_function(prompt: str):
    response = await call_api_async(prompt)
    return response
```

### Track Tokens

```python
from langsmith_config import token_tracker

token_tracker.log_usage(
    service="MyService",
    operation="my_operation",
    model="gemini-2.5-flash",
    input_tokens=100,
    output_tokens=200,
    user_id="user123",
    job_id="job456"
)
```

---

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/token-usage` | GET | Get token usage summary |
| `/analytics/usage-history` | GET | Get detailed usage history |
| `/analytics/cost-breakdown` | GET | Get cost breakdown by service |
| `/analytics/langsmith-traces` | GET | Get LangSmith trace URLs |
| `/analytics/model-performance` | GET | Get performance metrics |

### Example Request

```bash
curl "http://localhost:8000/analytics/token-usage?user_id=user123"
```

### Example Response

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
    }
  }
}
```

---

## 💰 Pricing (Update as needed)

| Model | Input (per 1M) | Output (per 1M) |
|-------|----------------|-----------------|
| gemini-2.5-flash | $0.075 | $0.30 |
| gemini-3-pro-preview | $1.25 | $5.00 |
| gemini-2.0-flash-exp | Free | Free |

**Update in**: `langsmith_config.py` → `PRICING` dictionary

---

## 🎨 Dashboard

**File**: `frontend/analytics_dashboard.html`

**Setup**:
1. Update `API_BASE` to your backend URL
2. Open in browser
3. Enter user ID
4. Click "Load Analytics"

**Features**:
- 📊 Token usage charts
- 💵 Cost analysis
- 🔗 LangSmith trace links
- 📈 Service breakdown

---

## 🔍 Viewing Traces

### In LangSmith Dashboard

1. Go to https://smith.langchain.com/
2. Select project: **NexusAI**
3. Click on any trace
4. View waterfall timeline

### What You'll See

- ⏱️ **Timeline**: Visual execution flow
- 📥 **Inputs**: Prompts and parameters
- 📤 **Outputs**: Generated content
- 🎯 **Tokens**: Input/output breakdown
- 💰 **Cost**: Calculated cost
- 🏷️ **Metadata**: user_id, model, etc.

---

## 🎯 Common Patterns

### Pattern 1: Simple LLM Call

```python
@trace_llm_call(name="generate", service="MyService")
def generate(prompt: str):
    response = call_api(prompt)
    return response
```

### Pattern 2: Hierarchical Workflow

```python
from langsmith import traceable

@traceable(name="workflow", run_type="chain")
async def workflow(input: str):
    step1 = await process_step1(input)  # Child trace
    step2 = await process_step2(step1)  # Child trace
    return step2
```

### Pattern 3: Add Metadata

```python
from langsmith.run_helpers import get_current_run_tree

@trace_llm_call(name="generate", service="MyService")
def generate(prompt: str, user_id: str):
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.metadata.update({
            "user_id": user_id,
            "prompt_length": len(prompt)
        })
    
    response = call_api(prompt)
    return response
```

### Pattern 4: Error Handling

```python
@trace_llm_call(name="generate", service="MyService")
def generate(prompt: str):
    try:
        response = call_api(prompt)
        return response
    except Exception as e:
        run_tree = get_current_run_tree()
        if run_tree:
            run_tree.error = str(e)
        raise
```

---

## 📋 Integration Checklist

### Setup Phase
- [ ] Install: `pip install -r requirements.txt`
- [ ] Get API key from https://smith.langchain.com/
- [ ] Add `LANGSMITH_API_KEY` to `.env`
- [ ] Run: `python test_langsmith_setup.py`

### Code Phase
- [ ] Import: `from langsmith_config import trace_llm_call`
- [ ] Add decorators to LLM functions
- [ ] Add token tracking
- [ ] Add metadata (user_id, job_id)

### API Phase
- [ ] Import: `from analytics_api import router`
- [ ] Include router: `app.include_router(router)`
- [ ] Test endpoints

### Verification Phase
- [ ] Make test LLM calls
- [ ] Check LangSmith dashboard
- [ ] Verify analytics API
- [ ] Test dashboard UI

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "LANGSMITH_API_KEY not found" | Add to `.env` file |
| "Module 'langsmith' not found" | Run `pip install langsmith` |
| "Traces not appearing" | Wait a few seconds, check decorator |
| "Cost incorrect" | Update pricing in `langsmith_config.py` |
| "Dashboard not loading" | Update `API_BASE` URL |

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `langsmith_config.py` | Core integration module |
| `analytics_api.py` | REST API for analytics |
| `test_langsmith_setup.py` | Verification script |
| `frontend/analytics_dashboard.html` | Dashboard UI |
| `LANGSMITH_GUIDE.md` | Comprehensive guide |
| `LANGSMITH_IMPLEMENTATION.md` | Implementation summary |
| `LANGSMITH_ARCHITECTURE.md` | Architecture docs |

---

## 🔗 Quick Links

- **LangSmith Dashboard**: https://smith.langchain.com/
- **LangSmith Docs**: https://docs.smith.langchain.com/
- **Gemini Pricing**: https://ai.google.dev/pricing
- **Get API Key**: https://smith.langchain.com/settings

---

## 💡 Pro Tips

1. **Always add user_id** to metadata for filtering
2. **Use hierarchical tracing** for complex workflows
3. **Track all token usage** for accurate costs
4. **Add meaningful names** to traces
5. **Handle errors properly** with try/catch
6. **Update pricing regularly** as models change
7. **Monitor costs daily** to avoid surprises
8. **Use filters in LangSmith** to find specific traces

---

## 🎓 Learning Path

1. Read: `LANGSMITH_IMPLEMENTATION.md` (10 min)
2. Run: `python test_langsmith_setup.py` (2 min)
3. Study: `ImageGeneration/langsmith_integration_example.py` (15 min)
4. Integrate: Add to one service (30 min)
5. Test: Make calls and view traces (10 min)
6. Explore: LangSmith dashboard (20 min)

**Total Time**: ~90 minutes to full proficiency

---

## 📊 Success Metrics

After integration, you should see:
- ✅ Traces appearing in LangSmith dashboard
- ✅ Token usage tracked in analytics API
- ✅ Costs calculated correctly
- ✅ Dashboard showing real data
- ✅ Waterfall view showing operation flow

---

## 🚀 Next Level

Once basic integration is done:
1. Set up cost alerts in LangSmith
2. Create custom analytics reports
3. Implement A/B testing for prompts
4. Add performance monitoring
5. Export data for external analysis

---

**Need Help?** See `LANGSMITH_GUIDE.md` for detailed instructions!

---

**Version**: 1.0  
**Last Updated**: 2026-01-02  
**Status**: Production Ready ✅
