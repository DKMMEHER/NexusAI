# 🔑 GitHub Secrets Setup - Quick Guide

**Repository:** https://github.com/DKMMEHER/NexusAI  
**Secrets URL:** https://github.com/DKMMEHER/NexusAI/settings/secrets/actions

---

## ✅ Required Secrets Checklist

### Secret 1: GCP_SA_KEY
- [ ] **Name:** `GCP_SA_KEY`
- [ ] **Value:** Entire JSON content from your service account key file
- [ ] **Location:** Your service account key JSON file (e.g., `github-actions-key.json`)

**How to get:**
```bash
# If you have the key file, display its content:
cat path/to/your-service-account-key.json

# Copy ALL the JSON content and paste as the secret value
```

**Format:** Should be a complete JSON object like:
```json
{
  "type": "service_account",
  "project_id": "gen-lang-client-0250626520",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@gen-lang-client-0250626520.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

---

### Secret 2: GOOGLE_CLOUD_PROJECT
- [ ] **Name:** `GOOGLE_CLOUD_PROJECT`
- [ ] **Value:** `gen-lang-client-0250626520`

**Your Project ID:** `gen-lang-client-0250626520`

**Verify with:**
```bash
gcloud config get-value project
```

---

### Secret 3: GEMINI_API_KEY
- [ ] **Name:** `GEMINI_API_KEY`
- [ ] **Value:** Your Gemini API key

**How to get:**
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key or copy existing one
4. Paste the key as the secret value

**Format:** Should look like: `AIzaSy...` (starts with `AIza`)

---

### Secret 4: CLOUD_RUN_SUFFIX (Optional - Add Later)
- [ ] **Name:** `CLOUD_RUN_SUFFIX`
- [ ] **Value:** Your Cloud Run URL suffix (add after first deployment)

**Note:** You can skip this for now. After your first successful deployment, you'll get Cloud Run URLs like:
- `https://imagegeneration-abc123-uc.run.app`

The suffix would be: `abc123-uc`

You can add this secret later to enable health checks in the pipeline.

---

## 📋 Step-by-Step Instructions

### Step 1: Open GitHub Secrets Page
1. Go to: https://github.com/DKMMEHER/NexusAI/settings/secrets/actions
2. You should see the "Actions secrets and variables" page

### Step 2: Add Each Secret
For each secret above:

1. Click **"New repository secret"** button (green button on the right)
2. Enter the **Name** exactly as shown (case-sensitive!)
3. Paste the **Value** in the large text box
4. Click **"Add secret"**
5. Repeat for all secrets

### Step 3: Verify Secrets Added
After adding all secrets, you should see them listed:
- ✅ GCP_SA_KEY
- ✅ GOOGLE_CLOUD_PROJECT
- ✅ GEMINI_API_KEY
- ✅ CLOUD_RUN_SUFFIX (optional)

**Note:** You won't be able to see the values after adding them (GitHub hides them for security).

---

## 🧪 Testing After Setup

Once you've added the secrets:

### Option 1: Re-run Failed Workflow
1. Go to: https://github.com/DKMMEHER/NexusAI/actions
2. Click on the failed "CI/CD Pipeline" run
3. Click "Re-run all jobs" button
4. Watch it run with the new secrets!

### Option 2: Make a Small Commit
```bash
# Make a small change to trigger the pipeline
echo "# CI/CD Active" >> README.md
git add README.md
git commit -m "test: Trigger CI/CD with secrets configured"
git push origin main
```

---

## ⚠️ Important Notes

### Security Best Practices
- ✅ **NEVER** commit your service account key JSON file to Git
- ✅ **NEVER** share your secrets publicly
- ✅ GitHub secrets are encrypted and only accessible during workflow runs
- ✅ Add `*.json` and `*-key.json` to your `.gitignore`

### Troubleshooting

**If secrets don't work:**
1. Check the secret names are EXACTLY as shown (case-sensitive)
2. Verify the JSON is valid (use a JSON validator)
3. Make sure there are no extra spaces or newlines
4. Check the workflow logs for specific error messages

**If you don't have the service account key:**
```bash
# Create a new service account (if needed)
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions CI/CD" \
    --project=gen-lang-client-0250626520

# Grant permissions
export SA_EMAIL="github-actions@gen-lang-client-0250626520.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding gen-lang-client-0250626520 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding gen-lang-client-0250626520 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding gen-lang-client-0250626520 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding gen-lang-client-0250626520 \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create github-actions-key.json \
    --iam-account=$SA_EMAIL
```

---

## ✅ Success Criteria

Your secrets are correctly configured when:
- [ ] All 3-4 secrets are listed in GitHub
- [ ] Workflow run succeeds (no authentication errors)
- [ ] Tests pass in the pipeline
- [ ] Docker images build successfully
- [ ] Services deploy to Cloud Run

---

## 🚀 Next Steps

After adding secrets:
1. ✅ Re-run the failed workflow or push a new commit
2. ✅ Monitor the workflow execution (~15-18 minutes)
3. ✅ Verify all jobs complete successfully
4. ✅ Check Cloud Run for deployed services
5. ✅ Test the deployed services
6. ✅ Celebrate! 🎉

---

**Status:** 🔧 Ready to add secrets  
**Time Required:** 5 minutes  
**Difficulty:** Easy

---

*After adding these secrets, your CI/CD pipeline will be fully operational!*
