# 🚀 Deploying LangSmith Integration to Cloud Run

## ⚠️ Important: Why Traces Don't Appear on Cloud Run

You tested on: `https://director-962267416185.asia-south1.run.app/`

**The issue**: Your Cloud Run deployment is running the **OLD CODE** (before LangSmith integration).

**The solution**: Deploy the updated code with LangSmith integration.

---

## 📋 Deployment Checklist

### Step 1: Add Environment Variables to Cloud Run

Your Cloud Run service needs the LangSmith environment variables:

```bash
LANGSMITH_API_KEY=lsv2_pt_your_key_here
LANGSMITH_PROJECT=NexusAI
```

#### Option A: Using Google Cloud Console

1. Go to https://console.cloud.google.com/run
2. Click on your service (e.g., "director")
3. Click **"Edit & Deploy New Revision"**
4. Scroll to **"Variables & Secrets"**
5. Click **"Add Variable"**
6. Add:
   - Name: `LANGSMITH_API_KEY`
   - Value: `lsv2_pt_your_key_here`
7. Add another:
   - Name: `LANGSMITH_PROJECT`
   - Value: `NexusAI`
8. Click **"Deploy"**

#### Option B: Using gcloud CLI

```bash
gcloud run services update director \
  --region=asia-south1 \
  --update-env-vars LANGSMITH_API_KEY=lsv2_pt_your_key_here,LANGSMITH_PROJECT=NexusAI
```

---

### Step 2: Deploy Updated Code

Your code changes need to be deployed to Cloud Run.

#### If Using CI/CD (GitHub Actions):

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add LangSmith integration"
   git push origin main
   ```

2. **Wait for CI/CD to deploy** (check GitHub Actions)

3. **Verify deployment** in Cloud Run console

#### If Deploying Manually:

```bash
# Build and deploy
gcloud run deploy director \
  --source . \
  --region=asia-south1 \
  --platform=managed \
  --allow-unauthenticated
```

---

### Step 3: Verify Deployment

After deployment:

1. **Make a test request** to your Cloud Run URL
2. **Check LangSmith dashboard**: https://smith.langchain.com/
3. **Look for traces** with your user_id

---

## 🧪 Testing Locally First (Recommended)

Before deploying to Cloud Run, test locally to ensure everything works:

### Step 1: Run Service Locally

```bash
# Make sure .env file has:
# LANGSMITH_API_KEY=lsv2_pt_your_key_here
# LANGSMITH_PROJECT=NexusAI

# Run ImageGeneration service
python -m uvicorn ImageGeneration.backend:app --reload --port 8001
```

### Step 2: Run Test Script

```bash
python test_langsmith_integration.py
```

### Step 3: Check LangSmith

1. Go to https://smith.langchain.com/
2. Select project: **NexusAI**
3. Look for trace: **gemini_image_generation**
4. You should see the trace!

---

## 🔍 Troubleshooting

### Issue: "Traces still don't appear on Cloud Run"

**Check**:
1. ✅ Environment variables are set in Cloud Run
2. ✅ New code is deployed (check deployment timestamp)
3. ✅ Service restarted after adding env vars
4. ✅ No errors in Cloud Run logs

**View logs**:
```bash
gcloud run services logs read director --region=asia-south1 --limit=50
```

Look for:
- "LangSmith initialized" message
- Any LangSmith-related errors

### Issue: "Works locally but not on Cloud Run"

**Possible causes**:
1. Environment variables not set in Cloud Run
2. Old code still deployed
3. API key incorrect
4. Firewall/network issues

**Solution**:
- Double-check env vars in Cloud Run console
- Redeploy with latest code
- Check Cloud Run logs for errors

---

## 📊 Expected Results

### After Successful Deployment:

1. **Make request** to Cloud Run URL
2. **See trace** in LangSmith dashboard within seconds
3. **View details**:
   - Prompt used
   - Model called
   - Tokens consumed
   - Cost calculated
   - Duration

### Analytics API:

```bash
curl "https://your-service.run.app/analytics/token-usage?user_id=test_user"
```

Returns:
```json
{
  "total_tokens": 5000,
  "total_cost_usd": 0.015,
  "operations_count": 10,
  "by_service": {
    "ImageGeneration": {...}
  }
}
```

---

## 🎯 Quick Deployment Steps

### For Immediate Testing:

1. **Test locally first**:
   ```bash
   python test_langsmith_integration.py
   ```

2. **If local works, deploy to Cloud Run**:
   ```bash
   # Add env vars (see Step 1 above)
   # Then deploy
   git add .
   git commit -m "Add LangSmith integration"
   git push
   ```

3. **Wait for deployment** (~2-5 minutes)

4. **Test on Cloud Run**:
   - Make image generation request
   - Check LangSmith dashboard

---

## 💡 Pro Tips

1. **Test locally first** - Faster iteration, easier debugging
2. **Check logs** - Cloud Run logs show LangSmith initialization
3. **Use staging** - Test on staging environment before production
4. **Monitor costs** - LangSmith API calls are free, but monitor Gemini usage

---

## 📚 Related Files

- `test_langsmith_integration.py` - Local testing script
- `LANGSMITH_INTEGRATION_COMPLETE.md` - Integration status
- `LANGSMITH_GUIDE.md` - Comprehensive guide
- `.env.example` - Environment variable template

---

## ✅ Checklist

Before deploying to Cloud Run:

- [ ] Tested locally and traces appear in LangSmith
- [ ] `.env` file has correct `LANGSMITH_API_KEY`
- [ ] Code changes committed to git
- [ ] Environment variables added to Cloud Run
- [ ] Ready to deploy

---

**Status**: Ready to deploy  
**Next**: Test locally, then deploy to Cloud Run  
**Time**: ~10 minutes for full deployment
