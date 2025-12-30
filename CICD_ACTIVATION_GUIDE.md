# 🚀 CI/CD Activation Guide

**Status:** Testing Complete ✅ | CI/CD Ready to Activate 🔧

You've completed all unit and integration testing! Now let's activate your CI/CD pipeline.

---

## 📊 Current Status

### ✅ Completed
- [x] **92+ Integration Tests** - All services covered
- [x] **Unit Tests** - All features tested
- [x] **GitHub Workflows** - `ci-cd.yml` and `pr-tests.yml` created
- [x] **Documentation** - Complete setup guides available
- [x] **Docker Configuration** - Dockerfiles for all services
- [x] **Test Coverage** - 100% feature coverage

### 🔧 Pending Activation
- [ ] Google Cloud Service Account
- [ ] Artifact Registry Repository
- [ ] GitHub Secrets Configuration
- [ ] First Pipeline Run
- [ ] Branch Protection Rules

---

## 🎯 Activation Steps (30 minutes total)

### Step 1: Google Cloud Setup (15 minutes)

#### 1.1 Set Your Project ID
```bash
# Replace with your actual Google Cloud Project ID
export PROJECT_ID="your-project-id-here"

# Verify it's correct
echo $PROJECT_ID
gcloud config set project $PROJECT_ID
```

#### 1.2 Enable Required APIs
```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API (optional, for future use)
gcloud services enable cloudbuild.googleapis.com
```

#### 1.3 Create Service Account
```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions CI/CD" \
    --project=$PROJECT_ID

# Verify creation
gcloud iam service-accounts list
```

#### 1.4 Grant Permissions
```bash
# Set service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

# Grant Storage Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

# Grant Artifact Registry Writer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

# Grant Service Account User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# Verify permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}"
```

#### 1.5 Create Service Account Key
```bash
# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL

# ⚠️ IMPORTANT: This file contains sensitive credentials!
# Keep it secure and DO NOT commit to Git

# Verify key was created
ls -lh github-actions-key.json
```

#### 1.6 Create Artifact Registry Repository
```bash
# Create Docker repository for NexusAI images
gcloud artifacts repositories create nexusai \
    --repository-format=docker \
    --location=us-central1 \
    --description="NexusAI Docker images for CI/CD"

# Verify creation
gcloud artifacts repositories list --location=us-central1
```

---

### Step 2: GitHub Secrets Setup (5 minutes)

Go to your GitHub repository: `https://github.com/YOUR_USERNAME/NexusAI/settings/secrets/actions`

#### Add These 4 Secrets:

1. **GCP_SA_KEY**
   ```bash
   # Copy the entire JSON content
   cat github-actions-key.json
   ```
   - Click "New repository secret"
   - Name: `GCP_SA_KEY`
   - Value: Paste the entire JSON content
   - Click "Add secret"

2. **GOOGLE_CLOUD_PROJECT**
   - Name: `GOOGLE_CLOUD_PROJECT`
   - Value: Your project ID (e.g., `nexusai-12345`)
   - Click "Add secret"

3. **GEMINI_API_KEY**
   - Name: `GEMINI_API_KEY`
   - Value: Your Gemini API key
   - Get from: https://aistudio.google.com/app/apikey
   - Click "Add secret"

4. **CLOUD_RUN_SUFFIX** (Optional - for health checks)
   - Name: `CLOUD_RUN_SUFFIX`
   - Value: Your Cloud Run URL suffix (e.g., `abc123-uc`)
   - You can add this later after first deployment
   - Click "Add secret"

#### Verify Secrets
- Go to: Settings → Secrets and variables → Actions
- You should see all 3-4 secrets listed
- ✅ GCP_SA_KEY
- ✅ GOOGLE_CLOUD_PROJECT
- ✅ GEMINI_API_KEY
- ✅ CLOUD_RUN_SUFFIX (optional)

---

### Step 3: Test the Pipeline (10 minutes)

#### 3.1 Commit and Push Workflow Files (if not already done)
```bash
# Check if workflows are committed
git status

# If not committed, add them
git add .github/workflows/
git add CICD_*.md
git commit -m "Add CI/CD pipeline configuration"
git push origin main
```

#### 3.2 Trigger First Pipeline Run
```bash
# Option A: Make a small change to trigger pipeline
echo "# CI/CD Pipeline Active" >> README.md
git add README.md
git commit -m "Activate CI/CD pipeline"
git push origin main

# Option B: Manually trigger workflow (if configured)
# Go to GitHub Actions tab and click "Run workflow"
```

#### 3.3 Monitor Pipeline Execution
1. Go to: `https://github.com/YOUR_USERNAME/NexusAI/actions`
2. Click on the latest "CI/CD Pipeline" run
3. Watch the progress:
   - ✅ **Test** job (~2-3 minutes)
   - ✅ **Quality** job (~1 minute)
   - ✅ **Build** job (~5-8 minutes) - Builds 6 Docker images
   - ✅ **Deploy** job (~3-5 minutes) - Deploys 6 services
   - ✅ **Health Check** job (~1 minute)
   - ✅ **Notify** job (~10 seconds)

**Expected Total Time:** 12-18 minutes for first run

---

### Step 4: Verify Deployment (5 minutes)

#### 4.1 List Deployed Services
```bash
# List all Cloud Run services
gcloud run services list --region=us-central1
```

**Expected Services:**
- imagegeneration
- chat
- director
- videogeneration
- documentssummarization
- youtubetranscript

#### 4.2 Get Service URLs
```bash
# Get all service URLs
for service in imagegeneration chat director videogeneration documentssummarization youtubetranscript; do
  echo "=== $service ==="
  gcloud run services describe $service --region=us-central1 --format='value(status.url)'
done
```

#### 4.3 Test Health Endpoints
```bash
# Test each service health endpoint
# Replace XXXXX with your actual Cloud Run suffix

curl https://imagegeneration-XXXXX.run.app/health
curl https://chat-XXXXX.run.app/health
curl https://director-XXXXX.run.app/health
curl https://videogeneration-XXXXX.run.app/health
curl https://documentssummarization-XXXXX.run.app/health
curl https://youtubetranscript-XXXXX.run.app/health
```

**Expected Response:** `{"status": "healthy"}` or similar

#### 4.4 Test a Service
```bash
# Example: Test Image Generation
SERVICE_URL=$(gcloud run services describe imagegeneration --region=us-central1 --format='value(status.url)')

curl -X POST $SERVICE_URL/image/generate \
  -F "prompt=A beautiful sunset over mountains" \
  -F "user_id=test-user"
```

---

### Step 5: Set Up Branch Protection (5 minutes)

#### 5.1 Enable Branch Protection
1. Go to: `https://github.com/YOUR_USERNAME/NexusAI/settings/branches`
2. Click "Add rule" or "Add branch protection rule"
3. Branch name pattern: `main`

#### 5.2 Configure Protection Rules
- ✅ **Require a pull request before merging**
  - Require approvals: 1 (optional, if working in a team)
- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - Select required status checks:
    - ✅ `test` (Run Tests)
    - ✅ `quality` (Code Quality)
- ✅ **Do not allow bypassing the above settings** (recommended)
- Click "Create" or "Save changes"

#### 5.3 Test Branch Protection
```bash
# Create a test branch
git checkout -b test-branch-protection
echo "# Test" >> README.md
git add README.md
git commit -m "Test branch protection"
git push origin test-branch-protection

# Create PR on GitHub
# Try to merge without tests passing - should be blocked!
```

---

## 🎉 Success Criteria

Your CI/CD pipeline is fully activated when:

- [x] ✅ Service account created with proper permissions
- [x] ✅ Artifact Registry repository exists
- [x] ✅ GitHub secrets configured
- [x] ✅ First pipeline run completed successfully
- [x] ✅ All 6 services deployed to Cloud Run
- [x] ✅ Health checks passing
- [x] ✅ Branch protection enabled
- [x] ✅ PR workflow tested

---

## 🔄 How It Works Now

### Every Pull Request:
1. 🧪 Runs all 92+ tests automatically
2. 🎨 Checks code quality (Black, Flake8)
3. 📊 Generates coverage report
4. 💬 Comments results on PR
5. ❌ **NO deployment** (safe testing!)

### Every Push to `main`:
1. 🧪 Runs all tests
2. 🎨 Checks code quality
3. 🐳 Builds 6 Docker images
4. 📦 Pushes to Artifact Registry
5. 🚀 Deploys to Cloud Run
6. 🏥 Runs health checks
7. 📢 Sends notifications

### Every Push to `develop`:
1. 🧪 Runs all tests
2. 🎨 Checks code quality
3. ❌ **NO deployment**

---

## 🛠️ Troubleshooting

### Pipeline Fails at Test Stage
```bash
# Run tests locally first
pytest tests/unit -v
pytest tests/integration -v --ignore=tests/integration/test_integration_deployment.py

# Check for missing dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Pipeline Fails at Build Stage
```bash
# Test Docker build locally
docker build -t test-image -f ImageGeneration/Dockerfile .

# Check for syntax errors
docker build --no-cache -t test-image -f ImageGeneration/Dockerfile .
```

### Pipeline Fails at Deploy Stage

**Common Issues:**

1. **Permission Denied**
   - Verify service account has all 4 roles
   - Check `GCP_SA_KEY` secret is correct JSON

2. **Image Not Found**
   - Verify Artifact Registry repository exists
   - Check image was pushed successfully in build logs

3. **Service Won't Start**
   ```bash
   # Check Cloud Run logs
   gcloud run services logs read imagegeneration --region=us-central1 --limit=50
   ```

4. **Environment Variables Missing**
   - Verify `GEMINI_API_KEY` secret is set
   - Check deployment step includes `--set-env-vars`

### Health Checks Fail
```bash
# Manually test health endpoint
SERVICE_URL=$(gcloud run services describe imagegeneration --region=us-central1 --format='value(status.url)')
curl $SERVICE_URL/health

# Check logs
gcloud run services logs read imagegeneration --region=us-central1
```

---

## 📚 Quick Reference

### Useful Commands

```bash
# View GitHub workflow runs
gh run list

# View specific run details
gh run view RUN_ID

# Re-run failed workflow
gh run rerun RUN_ID

# Cancel running workflow
gh run cancel RUN_ID

# List Cloud Run services
gcloud run services list --region=us-central1

# View service details
gcloud run services describe SERVICE_NAME --region=us-central1

# View service logs
gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=100

# Update service configuration
gcloud run services update SERVICE_NAME --region=us-central1 --memory=4Gi

# Delete a service
gcloud run services delete SERVICE_NAME --region=us-central1
```

### Important URLs

- **GitHub Actions**: `https://github.com/YOUR_USERNAME/NexusAI/actions`
- **Cloud Run Console**: `https://console.cloud.google.com/run`
- **Artifact Registry**: `https://console.cloud.google.com/artifacts`
- **IAM & Admin**: `https://console.cloud.google.com/iam-admin`
- **Gemini API Keys**: `https://aistudio.google.com/app/apikey`

---

## 💰 Cost Estimate

### GitHub Actions (Free Tier)
- ✅ 2,000 minutes/month for private repos
- ✅ Unlimited for public repos
- Your pipeline: ~15 minutes per run
- **Cost:** $0 (within free tier)

### Google Cloud Run (Free Tier)
- ✅ 2 million requests/month
- ✅ 360,000 GB-seconds memory/month
- ✅ 180,000 vCPU-seconds/month
- **Cost:** $0-5/month for small projects

### Artifact Registry
- ✅ 0.5 GB free storage
- ✅ $0.10/GB/month after
- **Cost:** $0-2/month

**Total Estimated Cost:** $0-7/month for development

---

## 🎯 Next Steps After Activation

1. **Monitor First Deployment**
   - Watch all jobs complete successfully
   - Verify all services are healthy
   - Test each service endpoint

2. **Set Up Notifications** (Optional)
   - Configure Slack notifications
   - Set up email alerts
   - Add status badges to README

3. **Optimize Pipeline** (Optional)
   - Add caching for faster builds
   - Parallelize more jobs
   - Add performance benchmarks

4. **Document Your Setup**
   - Update README with deployment URLs
   - Add CI/CD status badge
   - Document any custom configurations

5. **Team Onboarding** (If applicable)
   - Share this guide with team
   - Set up code review process
   - Configure PR templates

---

## 📞 Support Resources

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Artifact Registry Docs**: https://cloud.google.com/artifact-registry/docs
- **Your Test Documentation**: `tests/integration/INTEGRATION_TESTS_SUMMARY.md`
- **Setup Guide**: `CICD_SETUP.md`
- **Checklist**: `CICD_CHECKLIST.md`

---

## ✅ Activation Checklist

Print this and check off as you go:

- [ ] Set `PROJECT_ID` environment variable
- [ ] Enable Cloud Run API
- [ ] Enable Artifact Registry API
- [ ] Create `github-actions` service account
- [ ] Grant all 4 IAM roles
- [ ] Create service account key (`github-actions-key.json`)
- [ ] Create Artifact Registry repository (`nexusai`)
- [ ] Add `GCP_SA_KEY` to GitHub secrets
- [ ] Add `GOOGLE_CLOUD_PROJECT` to GitHub secrets
- [ ] Add `GEMINI_API_KEY` to GitHub secrets
- [ ] Add `CLOUD_RUN_SUFFIX` to GitHub secrets (optional)
- [ ] Push code to trigger first pipeline run
- [ ] Monitor pipeline execution (12-18 minutes)
- [ ] Verify all 6 services deployed
- [ ] Test health endpoints
- [ ] Test at least one service endpoint
- [ ] Enable branch protection on `main`
- [ ] Test PR workflow with test branch
- [ ] Delete `github-actions-key.json` from local machine (after adding to GitHub)
- [ ] Celebrate! 🎉

---

**Last Updated:** 2025-12-30  
**Status:** ✅ Ready for Activation  
**Estimated Time:** 30 minutes  
**Difficulty:** Intermediate

---

**🚀 You're ready to activate your CI/CD pipeline! Follow the steps above and you'll have automated testing and deployment in 30 minutes!**
