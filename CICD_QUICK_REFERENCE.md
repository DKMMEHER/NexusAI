# 🚀 CI/CD Quick Reference

## 📋 What Was Created

✅ **`.github/workflows/ci-cd.yml`** - Main CI/CD pipeline  
✅ **`.github/workflows/pr-tests.yml`** - PR testing workflow  
✅ **`CICD_SETUP.md`** - Detailed setup guide  
✅ **`CICD_CHECKLIST.md`** - Step-by-step checklist  
✅ **`CICD_QUICK_REFERENCE.md`** - This file  

---

## ⚡ Quick Start (30 minutes)

### 1. Set Up Google Cloud (10 min)
```bash
# Set your project
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions --project=$PROJECT_ID

# Grant permissions (run all 4 commands from CICD_SETUP.md)

# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Create Artifact Registry
gcloud artifacts repositories create nexusai \
    --repository-format=docker \
    --location=us-central1
```

### 2. Set Up GitHub Secrets (5 min)
Go to: `Settings → Secrets → Actions → New repository secret`

Add these 3 secrets:
1. **GCP_SA_KEY** = Contents of `github-actions-key.json`
2. **GOOGLE_CLOUD_PROJECT** = Your project ID
3. **GEMINI_API_KEY** = Your Gemini API key

### 3. Push and Deploy (15 min)
```bash
git add .github/ CICD*.md
git commit -m "Add CI/CD pipeline"
git push origin main
```

Watch at: `https://github.com/YOUR_USERNAME/NexusAI/actions`

---

## 🎯 What Happens When

### On Push to `main`:
1. ✅ Run all 80+ tests (1 min)
2. ✅ Check code quality (30 sec)
3. ✅ Build 6 Docker images (3 min)
4. ✅ Deploy to Cloud Run (2 min)
5. ✅ Run health checks (30 sec)

**Total time:** ~7-10 minutes

### On Pull Request:
1. ✅ Run all tests (1 min)
2. ✅ Check code quality (30 sec)
3. ✅ Comment results on PR
4. ❌ **NO deployment**

**Total time:** ~2 minutes

---

## 🔧 Common Commands

### View Workflow Runs
```bash
# List recent runs
gh run list

# View specific run
gh run view

# Watch live
gh run watch
```

### Check Deployment
```bash
# List services
gcloud run services list --region=us-central1

# Get service URL
gcloud run services describe SERVICE_NAME --region=us-central1 --format='value(status.url)'

# View logs
gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=50
```

### Test Locally First
```bash
# Run tests
pytest tests/

# Check formatting
black --check .

# Lint
flake8 .
```

---

## 🎨 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Push to main                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼────┐              ┌────▼────┐
   │  Tests  │              │ Quality │
   └────┬────┘              └────┬────┘
        │                         │
        └────────────┬────────────┘
                     │
                ┌────▼────┐
                │  Build  │
                └────┬────┘
                     │
                ┌────▼────┐
                │ Deploy  │
                └────┬────┘
                     │
                ┌────▼────┐
                │ Health  │
                └────┬────┘
                     │
                ┌────▼────┐
                │ Notify  │
                └─────────┘
```

---

## 📊 Pipeline Status

Check status at: `https://github.com/YOUR_USERNAME/NexusAI/actions`

### Status Badges

Add to your README.md:

```markdown
![CI/CD](https://github.com/YOUR_USERNAME/NexusAI/workflows/CI/CD%20Pipeline/badge.svg)
![Tests](https://github.com/YOUR_USERNAME/NexusAI/workflows/Pull%20Request%20Tests/badge.svg)
```

---

## 🆘 Troubleshooting

### Tests Fail
```bash
# Run locally
pytest tests/unit -v
pytest tests/integration -v
```

### Build Fails
```bash
# Test Docker build
docker build -t test -f ImageGeneration/Dockerfile .
```

### Deploy Fails
```bash
# Check permissions
gcloud projects get-iam-policy $PROJECT_ID

# Check logs
gcloud run services logs read SERVICE_NAME --region=us-central1
```

---

## 💰 Costs

### GitHub Actions
- ✅ **Free:** 2,000 minutes/month (private repos)
- ✅ **Free:** Unlimited (public repos)
- Your usage: ~7 min per deployment

### Cloud Run
- ✅ **Free tier:** 2M requests/month
- ✅ **Free tier:** 360,000 GB-seconds/month
- Estimated: **$0-5/month** for small projects

---

## 🎯 Success Checklist

- [ ] GitHub secrets configured
- [ ] First deployment successful
- [ ] All services healthy
- [ ] Branch protection enabled
- [ ] Team members added
- [ ] Monitoring set up

---

## 📚 Documentation

- **Detailed Setup:** `CICD_SETUP.md`
- **Step-by-Step:** `CICD_CHECKLIST.md`
- **This Guide:** `CICD_QUICK_REFERENCE.md`

---

## 🎉 You're All Set!

Your NexusAI project now has:
- ✅ Automated testing
- ✅ Automated deployment
- ✅ Code quality checks
- ✅ Health monitoring
- ✅ Professional workflow

**Happy coding!** 🚀
