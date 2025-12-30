# ✅ CI/CD Setup Checklist

Use this checklist to set up your CI/CD pipeline step by step.

---

## 📋 Pre-Setup (5 minutes)

- [ ] GitHub repository created for NexusAI
- [ ] Google Cloud Project exists
- [ ] Cloud Run API enabled
- [ ] Artifact Registry API enabled
- [ ] You have `gcloud` CLI installed
- [ ] You have GitHub CLI (`gh`) installed (optional)

---

## 🔐 Google Cloud Setup (10 minutes)

### 1. Create Service Account

```bash
export PROJECT_ID="YOUR_PROJECT_ID"  # ⚠️ CHANGE THIS
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions CI/CD" \
    --project=$PROJECT_ID
```

- [ ] Service account created

### 2. Grant Permissions

```bash
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

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

- [ ] All 4 roles granted

### 3. Create Service Account Key

```bash
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL
```

- [ ] Key file `github-actions-key.json` created
- [ ] ⚠️ File is in a secure location

### 4. Create Artifact Registry

```bash
gcloud artifacts repositories create nexusai \
    --repository-format=docker \
    --location=us-central1 \
    --description="NexusAI Docker images"
```

- [ ] Artifact Registry repository created

---

## 🔑 GitHub Secrets Setup (5 minutes)

Go to: `https://github.com/YOUR_USERNAME/NexusAI/settings/secrets/actions`

### Add These Secrets:

1. **GCP_SA_KEY**
   ```bash
   # Copy the entire content:
   cat github-actions-key.json
   ```
   - [ ] Secret added

2. **GOOGLE_CLOUD_PROJECT**
   ```
   Value: your-project-id
   ```
   - [ ] Secret added

3. **GEMINI_API_KEY**
   ```
   Value: your-gemini-api-key
   ```
   - [ ] Secret added

4. **CLOUD_RUN_SUFFIX** (Optional)
   ```
   Value: abc123-uc  # From your Cloud Run URL
   ```
   - [ ] Secret added (or skipped)

---

## 📝 Workflow Files (Already Created!)

- [x] `.github/workflows/ci-cd.yml` - Main CI/CD pipeline
- [x] `.github/workflows/pr-tests.yml` - PR testing workflow
- [x] `CICD_SETUP.md` - Detailed setup guide
- [x] `CICD_CHECKLIST.md` - This checklist

---

## 🧪 Test the Pipeline (10 minutes)

### 1. Commit and Push Workflow Files

```bash
git add .github/workflows/
git add CICD_SETUP.md CICD_CHECKLIST.md
git commit -m "Add CI/CD pipeline"
git push origin main
```

- [ ] Files committed and pushed

### 2. Check GitHub Actions

Go to: `https://github.com/YOUR_USERNAME/NexusAI/actions`

- [ ] Workflow run started
- [ ] Tests are running
- [ ] No errors in logs

### 3. Wait for Completion

Expected time: 5-10 minutes for first run

- [ ] All tests passed ✅
- [ ] Docker images built ✅
- [ ] Services deployed ✅
- [ ] Health checks passed ✅

---

## 🎯 Verify Deployment (5 minutes)

### 1. List Deployed Services

```bash
gcloud run services list --region=us-central1
```

Expected services:
- [ ] imagegeneration
- [ ] chat
- [ ] director
- [ ] videogeneration
- [ ] documentssummarization
- [ ] youtubetranscript

### 2. Test Health Endpoints

```bash
# Get URLs
gcloud run services describe imagegeneration --region=us-central1 --format='value(status.url)'

# Test health (replace URL)
curl https://imagegeneration-XXXXX.run.app/health
```

- [ ] All services respond with 200 OK

### 3. Test a Service

```bash
# Test image generation (example)
curl -X POST https://imagegeneration-XXXXX.run.app/image/generate \
  -F "prompt=A beautiful sunset" \
  -F "user_id=test"
```

- [ ] Service works correctly

---

## 🛡️ Set Up Branch Protection (5 minutes)

Go to: `https://github.com/YOUR_USERNAME/NexusAI/settings/branches`

### Add Rule for `main` Branch:

- [ ] Click "Add rule"
- [ ] Branch name pattern: `main`
- [ ] ✅ Require a pull request before merging
- [ ] ✅ Require status checks to pass before merging
- [ ] ✅ Require branches to be up to date before merging
- [ ] Select status checks:
  - [ ] `test` (Run Tests)
  - [ ] `quality` (Code Quality)
- [ ] Click "Create"

---

## 🎉 Final Verification

### Test the Full Workflow:

1. **Create a feature branch**
   ```bash
   git checkout -b feature/test-cicd
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test CI/CD"
   git push origin feature/test-cicd
   ```
   - [ ] Branch created and pushed

2. **Create Pull Request**
   - Go to GitHub
   - Create PR from `feature/test-cicd` to `main`
   - [ ] PR created
   - [ ] Tests run automatically
   - [ ] PR comment shows test results

3. **Merge PR**
   - [ ] Tests passed
   - [ ] PR approved (if required)
   - [ ] Merge PR
   - [ ] Full CI/CD pipeline runs
   - [ ] Deployment successful

---

## 📊 Success Criteria

Your CI/CD is working if:

- [x] ✅ Tests run on every push
- [x] ✅ Tests run on every PR
- [x] ✅ Code quality checks pass
- [x] ✅ Docker images build successfully
- [x] ✅ Services deploy to Cloud Run
- [x] ✅ Health checks pass
- [x] ✅ You can't merge failing PRs (if branch protection enabled)

---

## 🚀 You're Done!

**Congratulations!** Your CI/CD pipeline is now active!

### What Happens Now:

**Every time you push to `main`:**
1. ✅ All 80+ tests run automatically
2. ✅ Code quality is checked
3. ✅ Docker images are built
4. ✅ Services are deployed to Cloud Run
5. ✅ Health checks verify deployment
6. ✅ You get notified of any issues

**Every time you create a PR:**
1. ✅ All tests run
2. ✅ Code quality is checked
3. ✅ Results are commented on the PR
4. ❌ No deployment (safe!)

---

## 📚 Next Steps

- [ ] Read `CICD_SETUP.md` for detailed information
- [ ] Set up Slack/email notifications (optional)
- [ ] Configure monitoring and alerts
- [ ] Add more tests as you develop
- [ ] Celebrate! 🎉

---

## 🆘 Troubleshooting

**Tests failing?**
- Run locally first: `pytest tests/`
- Check GitHub Actions logs
- Review error messages

**Deployment failing?**
- Check service account permissions
- Verify GitHub secrets are correct
- Check Cloud Run logs

**Need help?**
- See `CICD_SETUP.md` for detailed troubleshooting
- Check GitHub Actions documentation
- Review Cloud Run documentation

---

## 📞 Quick Links

- **GitHub Actions**: https://github.com/YOUR_USERNAME/NexusAI/actions
- **Cloud Run Console**: https://console.cloud.google.com/run
- **Artifact Registry**: https://console.cloud.google.com/artifacts
- **Setup Guide**: `CICD_SETUP.md`

---

**Last Updated:** 2025-12-29  
**Status:** ✅ Ready to use
