# LangSmith Integration Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NexusAI Application                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│ Image        │      │ Chat         │     │ Director     │
│ Generation   │      │ Service      │     │ Service      │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        │ @trace_llm_call     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ langsmith_config │
                    │   - Tracing      │
                    │   - Token Track  │
                    │   - Cost Calc    │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ LangSmith│  │ Token    │  │ Analytics│
        │ Platform │  │ Tracker  │  │ API      │
        └──────────┘  └──────────┘  └──────────┘
                │                           │
                │                           ▼
                │                   ┌──────────────┐
                │                   │ Dashboard    │
                │                   │ (HTML)       │
                │                   └──────────────┘
                │
                ▼
        ┌──────────────────┐
        │ Waterfall View   │
        │ - Traces         │
        │ - Tokens         │
        │ - Costs          │
        │ - Performance    │
        └──────────────────┘
```

## Data Flow

### 1. LLM Call Flow

```
User Request
    │
    ▼
Service Endpoint (e.g., /generate)
    │
    ▼
@trace_llm_call decorator
    │
    ├─► LangSmith: Create trace
    │   └─► Record: inputs, metadata
    │
    ▼
LLM API Call (Gemini)
    │
    ▼
Response Processing
    │
    ├─► Extract tokens
    ├─► Calculate cost
    └─► Update trace
        │
        ├─► LangSmith: Add outputs, tokens, cost
        └─► TokenTracker: Log usage
            │
            ▼
Return to User
```

### 2. Analytics Flow

```
User Opens Dashboard
    │
    ▼
GET /analytics/token-usage
    │
    ▼
TokenTracker.get_summary()
    │
    ├─► Filter by user_id
    ├─► Aggregate tokens
    ├─► Calculate costs
    └─► Group by service
        │
        ▼
Return JSON
    │
    ▼
Dashboard Renders Charts
```

### 3. Trace Viewing Flow

```
User Clicks "View Trace"
    │
    ▼
GET /analytics/langsmith-traces
    │
    ▼
LangSmith Client API
    │
    ├─► List runs
    ├─► Filter by user_id
    └─► Get trace URLs
        │
        ▼
Return Trace Links
    │
    ▼
User Clicks Link
    │
    ▼
LangSmith Dashboard
    │
    └─► Waterfall View
        ├─► Timeline
        ├─► Inputs/Outputs
        ├─► Token Usage
        └─► Cost Analysis
```

## Component Interactions

### Tracing Decorator

```python
@trace_llm_call(name="operation", service="Service")
def my_function():
    # 1. Decorator creates LangSmith run
    # 2. Records inputs and metadata
    # 3. Executes function
    # 4. Records outputs and metrics
    # 5. Sends to LangSmith platform
    pass
```

### Token Tracker

```python
token_tracker.log_usage(
    service="ImageGeneration",
    operation="generate",
    model="gemini-2.5-flash",
    input_tokens=100,
    output_tokens=200,
    user_id="user123"
)

# Stores in memory:
# {
#   "timestamp": "2026-01-02T10:00:00",
#   "service": "ImageGeneration",
#   "total_tokens": 300,
#   "cost_usd": 0.000075
# }
```

### Analytics API

```python
# Aggregates data from TokenTracker
summary = token_tracker.get_summary(user_id="user123")

# Returns:
# {
#   "total_tokens": 15000,
#   "total_cost_usd": 0.0225,
#   "by_service": {
#     "ImageGeneration": {...},
#     "Chat": {...}
#   }
# }
```

## Waterfall Visualization

### Example Trace Hierarchy

```
create_movie (Total: 1200ms, Cost: $0.015)
│
├─► generate_script (500ms, $0.010)
│   ├─► Input: "Create a video about AI"
│   ├─► Model: gemini-3-pro-preview
│   ├─► Tokens: 1000 input, 2000 output
│   └─► Output: [Scene 1, Scene 2, Scene 3]
│
├─► generate_scenes (600ms, $0.004)
│   ├─► generate_scene_1 (200ms, $0.0013)
│   ├─► generate_scene_2 (200ms, $0.0013)
│   └─► generate_scene_3 (200ms, $0.0014)
│
└─► stitch_video (100ms, $0.001)
    └─► Output: final_video.mp4
```

### Metadata Captured

For each trace:
- **Inputs**: Prompts, parameters
- **Outputs**: Generated content
- **Tokens**: Input/output breakdown
- **Cost**: Calculated cost in USD
- **Duration**: Execution time
- **Model**: Which model was used
- **User Context**: user_id, job_id
- **Status**: Success/error
- **Error Details**: If failed

## Cost Calculation Formula

```
For each LLM call:

Input Cost = (input_tokens / 1,000,000) × input_price_per_1M
Output Cost = (output_tokens / 1,000,000) × output_price_per_1M
Total Cost = Input Cost + Output Cost

Example (gemini-2.5-flash):
- Input: 1000 tokens × $0.075/1M = $0.000075
- Output: 2000 tokens × $0.30/1M = $0.000600
- Total: $0.000675
```

## Integration Points

### 1. Service Level

```python
# In each service's backend.py
from langsmith_config import trace_llm_call

@trace_llm_call(name="service_operation", service="ServiceName")
def operation():
    # Your code
    pass
```

### 2. API Level

```python
# Add analytics router
from analytics_api import router as analytics_router
app.include_router(analytics_router)
```

### 3. Frontend Level

```html
<!-- Analytics Dashboard -->
<script>
  fetch('/analytics/token-usage?user_id=user123')
    .then(res => res.json())
    .then(data => renderCharts(data));
</script>
```

## Monitoring & Observability

### What You Can Monitor

1. **Token Usage**
   - Total tokens per user
   - Tokens per service
   - Tokens per model

2. **Costs**
   - Total cost per user
   - Cost per service
   - Cost per operation
   - Daily/weekly/monthly trends

3. **Performance**
   - Latency per operation
   - Success/failure rates
   - Error types and frequencies

4. **Usage Patterns**
   - Most used services
   - Most used models
   - Peak usage times
   - User behavior

### Alerts & Notifications

Set up in LangSmith:
- Cost threshold alerts
- Error rate alerts
- Latency alerts
- Token usage alerts

## Security & Privacy

### Data Handling

- **Traces**: Stored in LangSmith (encrypted)
- **Tokens**: Stored in memory (ephemeral)
- **User Data**: Filtered by user_id
- **API Keys**: Never logged in traces

### Access Control

- Analytics API requires authentication
- User can only view their own data
- LangSmith dashboard requires login

## Scalability

### Current Implementation

- **In-Memory Storage**: TokenTracker uses list
- **Suitable for**: Development, small deployments
- **Limitations**: Data lost on restart

### Production Recommendations

1. **Use Database**: Store token usage in Firestore/PostgreSQL
2. **Use Redis**: Cache analytics data
3. **Use Message Queue**: Async logging to LangSmith
4. **Use CDN**: Serve dashboard from CDN

## Future Enhancements

1. **Real-time Dashboard**: WebSocket updates
2. **Advanced Analytics**: ML-based insights
3. **Budget Management**: Set spending limits
4. **A/B Testing**: Compare prompts/models
5. **Custom Reports**: Export to PDF/Excel
6. **Alerting System**: Email/Slack notifications

---

This architecture provides complete observability for your LLM operations while maintaining performance and scalability.
