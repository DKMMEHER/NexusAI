# 🚀 CI/CD Pipeline Setup Guide

## Overview

This guide will help you set up automated testing and deployment for NexusAI using GitHub Actions.

**What you'll get:**
- ✅ Automated testing on every commit
- ✅ Automated deployment to Cloud Run
- ✅ Code quality checks
- ✅ Health monitoring
- ✅ PR test results

---

## Prerequisites

1. ✅ GitHub repository for NexusAI
2. ✅ Google Cloud Project with Cloud Run enabled
3. ✅ Artifact Registry repository created
4. ✅ Service account with appropriate permissions

---

## Step 1: Create Google Cloud Service Account

### 1.1 Create Service Account

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions CI/CD" \
    --project=$PROJECT_ID
```

### 1.2 Grant Permissions

```bash
# Get service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"
```

### 1.3 Create and Download Key

```bash
# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL

# The key will be saved as github-actions-key.json
# ⚠️ Keep this file secure! You'll need it for GitHub Secrets
```

---

## Step 2: Create Artifact Registry Repository

```bash
# Create repository for Docker images
gcloud artifacts repositories create nexusai \
    --repository-format=docker \
    --location=us-central1 \
    --description="NexusAI Docker images"
```

---

## Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets:

1. **`GCP_SA_KEY`**
   - Content: Entire contents of `github-actions-key.json`
   - How to get: `cat github-actions-key.json` and copy all content

2. **`GOOGLE_CLOUD_PROJECT`**
   - Content: Your Google Cloud Project ID
   - Example: `nexusai-12345`

3. **`GEMINI_API_KEY`**
   - Content: Your Gemini API key
   - Get from: https://aistudio.google.com/app/apikey

4. **`CLOUD_RUN_SUFFIX`** (Optional, for health checks)
   - Content: Your Cloud Run URL suffix
   - Example: `abc123-uc` (from `https://service-abc123-uc.run.app`)

### How to Add Secrets:

```
1. Go to: https://github.com/YOUR_USERNAME/NexusAI/settings/secrets/actions
2. Click "New repository secret"
3. Name: GCP_SA_KEY
4. Value: Paste entire JSON content from github-actions-key.json
5. Click "Add secret"
6. Repeat for other secrets
```

---

## Step 4: Update Workflow Configuration (if needed)

Edit `.github/workflows/ci-cd.yml` if you need to change:

### Region
```yaml
env:
  REGION: us-central1  # Change to your preferred region
```

### Service Ports
```yaml
strategy:
  matrix:
    service:
      - name: ImageGeneration
        port: 8001  # Update if different
```

### Resource Limits
```yaml
--memory 2Gi \
--cpu 2 \
--max-instances 10 \
```

---

## Step 5: Test the Pipeline

### 5.1 Push to a Feature Branch

```bash
git checkout -b test-ci-cd
git add .
git commit -m "Test CI/CD pipeline"
git push origin test-ci-cd
```

**Expected:** PR tests workflow runs (no deployment)

### 5.2 Create Pull Request

1. Go to GitHub
2. Create PR from `test-ci-cd` to `main`
3. Watch the tests run
4. Check for PR comment with results

### 5.3 Merge to Main

```bash
# After PR is approved
git checkout main
git merge test-ci-cd
git push origin main
```

**Expected:** Full CI/CD pipeline runs (tests + deployment)

---

## Step 6: Monitor the Pipeline

### View Workflow Runs

1. Go to: `https://github.com/YOUR_USERNAME/NexusAI/actions`
2. Click on the latest workflow run
3. Expand each job to see details

### Check Deployment

```bash
# List Cloud Run services
gcloud run services list --region=us-central1

# Get service URL
gcloud run services describe imagegeneration --region=us-central1 --format='value(status.url)'

# Test health endpoint
curl https://imagegeneration-XXXXX.run.app/health
```

---

## Workflow Behavior

### On Pull Request:
- ✅ Run unit tests
- ✅ Run integration tests
- ✅ Check code quality
- ✅ Generate coverage report
- ✅ Comment results on PR
- ❌ **NO deployment**

### On Push to Main:
- ✅ Run all tests
- ✅ Check code quality
- ✅ Build Docker images
- ✅ Push to Artifact Registry
- ✅ Deploy to Cloud Run
- ✅ Run health checks
- ✅ Send notification

### On Push to Develop:
- ✅ Run all tests
- ✅ Check code quality
- ❌ **NO deployment**

---

## Troubleshooting

### Tests Fail

```bash
# Run tests locally first
pytest tests/unit -v
pytest tests/integration -v --ignore=tests/integration/test_integration_deployment.py

# Check for missing dependencies
pip install -r requirements.txt
```

### Build Fails

```bash
# Test Docker build locally
docker build -t test-image -f ImageGeneration/Dockerfile .

# Check Dockerfile syntax
docker build --no-cache -t test-image -f ImageGeneration/Dockerfile .
```

### Deployment Fails

**Common issues:**

1. **Permission denied**
   - Check service account has `roles/run.admin`
   - Verify `GCP_SA_KEY` secret is correct

2. **Image not found**
   - Check Artifact Registry repository exists
   - Verify image was pushed successfully

3. **Service won't start**
   - Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME --region=us-central1`
   - Verify environment variables are set

### Health Check Fails

```bash
# Manually check service
curl https://YOUR-SERVICE-URL.run.app/health

# Check Cloud Run logs
gcloud run services logs read imagegeneration --region=us-central1 --limit=50
```

---

## Advanced Configuration

### Add Slack Notifications

Add to `.github/workflows/ci-cd.yml`:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Add Email Notifications

GitHub sends emails automatically for failed workflows to repository admins.

### Branch Protection Rules

1. Go to: Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Require pull request reviews

---

## Best Practices

### 1. Never Commit Secrets
```bash
# Add to .gitignore
echo "github-actions-key.json" >> .gitignore
echo "*.key" >> .gitignore
echo ".env" >> .gitignore
```

### 2. Test Locally First
```bash
# Before pushing
pytest tests/
black .
flake8 .
```

### 3. Use Feature Branches
```bash
# Always create feature branches
git checkout -b feature/new-feature
# Make changes
git push origin feature/new-feature
# Create PR
```

### 4. Review Logs
```bash
# Check Cloud Run logs regularly
gcloud run services logs read SERVICE_NAME --region=us-central1
```

### 5. Monitor Costs
```bash
# Check Cloud Run costs
gcloud billing accounts list
# View cost breakdown in Cloud Console
```

---

## Quick Reference

### Useful Commands

```bash
# View workflow runs
gh run list

# View specific run
gh run view RUN_ID

# Re-run failed jobs
gh run rerun RUN_ID

# Cancel running workflow
gh run cancel RUN_ID

# List Cloud Run services
gcloud run services list

# View service details
gcloud run services describe SERVICE_NAME --region=us-central1

# View logs
gcloud run services logs read SERVICE_NAME --region=us-central1

# Update service
gcloud run services update SERVICE_NAME --region=us-central1 --memory=4Gi
```

---

## Cost Optimization

### GitHub Actions (Free Tier)
- ✅ 2,000 minutes/month for private repos
- ✅ Unlimited for public repos
- ✅ Your tests run in ~1 minute

### Cloud Run
- ✅ Free tier: 2 million requests/month
- ✅ 360,000 GB-seconds memory/month
- ✅ 180,000 vCPU-seconds/month

### Artifact Registry
- ✅ 0.5 GB free storage
- ✅ $0.10/GB/month after that

**Estimated monthly cost:** $0-5 for small projects

---

## Next Steps

1. ✅ Set up GitHub secrets
2. ✅ Push code to trigger pipeline
3. ✅ Monitor first deployment
4. ✅ Set up branch protection
5. ✅ Add team members
6. ✅ Configure notifications

---

## Support

**Issues?**
- Check GitHub Actions logs
- Check Cloud Run logs
- Review this guide
- Check Google Cloud Console

**Need help?**
- GitHub Actions docs: https://docs.github.com/actions
- Cloud Run docs: https://cloud.google.com/run/docs
- NexusAI tests: `tests/integration/README.md`

---

**🎉 Congratulations! Your CI/CD pipeline is ready!**

Every push to `main` will now automatically:
1. Run all tests
2. Build Docker images
3. Deploy to Cloud Run
4. Verify health

**Happy deploying!** 🚀
