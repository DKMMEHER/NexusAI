# LangSmith Integration - Cloud Run Deployment

## ✅ What's Been Integrated

### Services with LangSmith:
1. **ImageGeneration** - Full tracing & token tracking
2. **Chat** - Full tracing & token tracking
3. **Director** - Script generation tracing

### Files Modified:
- `ImageGeneration/backend.py` - Added tracing decorators and token tracking
- `Chat/backend.py` - Added tracing decorators and token tracking
- `Director/backend.py` - Added tracing to script generation
- `langsmith_config.py` - Core LangSmith utilities (NEW)
- `analytics_api.py` - Analytics REST API (NEW)
- `requirements.txt` - Added langsmith and langchain packages

---

## 🔧 Required Environment Variables for Cloud Run

Add these to your Cloud Run service:

```bash
LANGSMITH_API_KEY=lsv2_pt_43...4783
LANGSMITH_PROJECT=NexusAI
```

**How to add**:
1. Go to https://console.cloud.google.com/run
2. Select your service
3. Click "Edit & Deploy New Revision"
4. Under "Variables & Secrets" → Add Variable
5. Add both variables above
6. Click "Deploy"

---

## 📦 Deployment Steps

### Step 1: Commit Changes
```bash
git add .
git commit -m "feat: Add LangSmith integration for LLM observability

- Added LangSmith tracing to ImageGeneration, Chat, and Director services
- Implemented token tracking and cost calculation
- Added analytics API endpoints
- Created comprehensive documentation
- Ready for Cloud Run deployment with LANGSMITH_API_KEY env var"
git push origin main
```

### Step 2: Wait for CI/CD
- GitHub Actions will automatically deploy to Cloud Run
- Check deployment status in GitHub Actions tab
- Wait ~3-5 minutes for deployment

### Step 3: Verify Deployment
1. Check Cloud Run console for new revision
2. Make a test request through your app
3. Check LangSmith dashboard: https://smith.langchain.com/

---

## 🧪 Testing After Deployment

### Test Image Generation:
1. Go to your app: https://director-962267416185.asia-south1.run.app/
2. Navigate to Image Generation
3. Generate an image
4. Go to https://smith.langchain.com/
5. Select project "NexusAI"
6. See the trace "gemini_image_generation"!

### Test Chat:
1. Go to Chat feature
2. Send a message
3. Check LangSmith for "chat_completion" trace

### Test Analytics API:
```bash
curl "https://director-962267416185.asia-south1.run.app/analytics/token-usage?user_id=YOUR_USER_ID" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

---

## 📊 What You'll See in LangSmith

### For Each Image Generation:
- Trace name: `gemini_image_generation`
- Service: `ImageGeneration`
- Prompt used
- Model: `gemini-2.5-flash-image`
- Tokens: Input/output breakdown
- Cost: Calculated in USD
- Duration: Execution time

### For Each Chat Message:
- Trace name: `chat_completion`
- Service: `Chat`
- User message
- AI response
- Tokens used
- Tools called (if any)

---

## ✅ Deployment Checklist

- [x] LangSmith integration code complete
- [x] Dependencies added to requirements.txt
- [ ] Environment variables added to Cloud Run
- [ ] Code committed to git
- [ ] Code pushed to trigger deployment
- [ ] Deployment completed
- [ ] Test request made
- [ ] Traces visible in LangSmith

---

## 🎯 Expected Timeline

- **Commit & Push**: 1 minute
- **CI/CD Deployment**: 3-5 minutes
- **First Trace**: Immediate after first request
- **Total Time**: ~10 minutes

---

## 💡 Important Notes

1. **Environment Variables**: Must be added to Cloud Run BEFORE or AFTER deployment
2. **No Code Changes Needed**: Everything is ready in the code
3. **Backward Compatible**: Works with or without LangSmith (graceful degradation)
4. **Zero Downtime**: Deployment won't affect existing functionality

---

Ready to deploy! 🚀
