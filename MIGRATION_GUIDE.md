# 🔄 Migration Guide: Old App → New CI/CD App

**Status:** 📋 **MIGRATION PLAN**  
**Goal:** Replace old manual deployment with new CI/CD-managed deployment  
**Custom Domain:** Will be remapped to new services

---

## 🎯 **Current Situation:**

### **Old Deployment (Manual):**
```
✅ Cloud Run services (manually deployed)
✅ Custom DNS mapped to old services
✅ Working in production
❌ No CI/CD pipeline
❌ Manual deployments
❌ Hard to maintain
```

### **New Deployment (CI/CD):**
```
🔄 Cloud Run services (CI/CD managed)
⏳ Not yet mapped to custom DNS
✅ Automated testing
✅ Automated deployments
✅ Easy to maintain
✅ Individual Dockerfiles
```

---

## 📋 **Migration Strategy:**

### **Phase 1: Deploy New Services (IN PROGRESS)**

**Current Step:** CI/CD pipeline is deploying new services

**New Service Names:**
```
imagegeneration-xxx.run.app
chat-xxx.run.app
director-xxx.run.app
videogeneration-xxx.run.app
documentssummarization-xxx.run.app
youtubetranscript-xxx.run.app
```

**Wait for:** All 6 services to deploy successfully (~10-12 minutes)

---

### **Phase 2: Test New Services**

Before switching DNS, verify new services work:

**1. Test Each Service:**
```bash
# Get service URLs
gcloud run services list --region=us-central1

# Test health endpoints
curl https://imagegeneration-xxx.run.app/health
curl https://chat-xxx.run.app/health
curl https://director-xxx.run.app/health
curl https://videogeneration-xxx.run.app/health
curl https://documentssummarization-xxx.run.app/health
curl https://youtubetranscript-xxx.run.app/health
```

**2. Test Frontend:**
- Visit: `https://director-xxx.run.app`
- Should load the React app
- Test creating an image
- Test chat functionality
- Test video generation

**3. Verify Everything Works:**
- ✅ All services respond
- ✅ Frontend loads
- ✅ API calls work
- ✅ Database connections work

---

### **Phase 3: Remap Custom Domain**

Once new services are verified:

**1. Get New Service URLs:**
```bash
gcloud run services describe director --region=us-central1 --format='value(status.url)'
gcloud run services describe imagegeneration --region=us-central1 --format='value(status.url)'
# ... repeat for all services
```

**2. Update DNS Mappings:**

**Option A: Using Cloud Run Domain Mappings**
```bash
# Remove old mappings
gcloud run domain-mappings delete --domain=yourdomain.com --region=us-central1

# Add new mappings
gcloud run services update director \
  --region=us-central1 \
  --add-custom-domain=yourdomain.com

gcloud run services update imagegeneration \
  --region=us-central1 \
  --add-custom-domain=images.yourdomain.com

# ... repeat for all services
```

**Option B: Using DNS Provider**
Update CNAME records in your DNS provider:
```
Before:
yourdomain.com → old-director-xxx.run.app

After:
yourdomain.com → director-xxx.run.app (new)
```

**3. Wait for DNS Propagation:**
- DNS changes take 5-30 minutes
- Test with: `nslookup yourdomain.com`

---

### **Phase 4: Verify Migration**

**1. Test Custom Domain:**
```bash
# Should hit new services
curl https://yourdomain.com/health
curl https://images.yourdomain.com/health
```

**2. Monitor Logs:**
```bash
# Check new services are receiving traffic
gcloud run services logs read director --region=us-central1 --limit=50
```

**3. Verify in Browser:**
- Visit your custom domain
- Should load new deployment
- Test all functionality

---

### **Phase 5: Clean Up Old Services**

**Only after verifying new services work!**

**1. List Old Services:**
```bash
gcloud run services list --region=us-central1
```

**2. Delete Old Services:**
```bash
# Delete old manually-deployed services
gcloud run services delete old-service-name --region=us-central1

# Example:
gcloud run services delete old-director --region=us-central1
gcloud run services delete old-imagegeneration --region=us-central1
# ... etc
```

**3. Clean Up Old Images:**
```bash
# List images in Artifact Registry
gcloud artifacts docker images list us-central1-docker.pkg.dev/gen-lang-client-0250626520/nexusai-repo

# Delete old images if needed
gcloud artifacts docker images delete IMAGE_PATH
```

---

## 🎯 **Step-by-Step Checklist:**

### **Now (Deployment Phase):**
- [x] Create individual Dockerfiles
- [x] Fix CI/CD workflow
- [x] Configure GitHub Secrets
- [x] Fix Artifact Registry repository name
- [ ] Wait for CI/CD deployment to complete (~10 min)

### **After Deployment:**
- [ ] Verify all 6 new services are running
- [ ] Test each service's health endpoint
- [ ] Test frontend on new director service
- [ ] Test all features work
- [ ] Note down new service URLs

### **DNS Migration:**
- [ ] Update custom domain mappings
- [ ] Point DNS to new services
- [ ] Wait for DNS propagation (5-30 min)
- [ ] Verify custom domain loads new app
- [ ] Monitor for any issues

### **Cleanup:**
- [ ] Keep old services running for 24-48 hours (safety)
- [ ] Monitor new services for stability
- [ ] Delete old services
- [ ] Clean up old Docker images
- [ ] Update documentation

---

## 🔄 **Rollback Plan (If Needed):**

If something goes wrong with new services:

**Quick Rollback:**
```bash
# Remap DNS back to old services
gcloud run domain-mappings delete --domain=yourdomain.com --region=us-central1

# Re-add old mapping
gcloud run services update old-director \
  --region=us-central1 \
  --add-custom-domain=yourdomain.com
```

**Why Keep Old Services:**
- Safety net during migration
- Can quickly rollback if issues
- Delete only after 24-48 hours of stability

---

## 📊 **Comparison:**

### **Old Deployment:**
```
Deployment Method: Manual
Update Process: Manual docker build + push + deploy
Testing: Manual
Rollback: Manual
Maintenance: High effort
```

### **New Deployment:**
```
Deployment Method: Automated (CI/CD)
Update Process: git push → automatic deploy
Testing: Automated (122 tests)
Rollback: git revert → automatic redeploy
Maintenance: Low effort
```

---

## 🎉 **Benefits After Migration:**

1. **Automated Deployments:**
   - Push code → Auto deploy
   - No manual steps

2. **Automated Testing:**
   - 122 tests run automatically
   - Catch bugs before deployment

3. **Easy Rollback:**
   - `git revert` → Auto redeploy old version
   - No manual intervention

4. **Better Monitoring:**
   - GitHub Actions shows deployment status
   - Easy to see what's deployed

5. **Team Collaboration:**
   - Other developers can contribute
   - CI/CD ensures quality

---

## ⏰ **Timeline:**

```
Now:           CI/CD deploying new services
+10-12 min:    New services deployed
+15 min:       Test new services
+30 min:       Update DNS mappings
+1 hour:       DNS propagated, new app live
+24-48 hours:  Monitor stability
+2 days:       Delete old services
```

---

## 📞 **Quick Commands:**

**Check Deployment Status:**
```bash
gcloud run services list --region=us-central1
```

**Get Service URL:**
```bash
gcloud run services describe SERVICE_NAME --region=us-central1 --format='value(status.url)'
```

**View Logs:**
```bash
gcloud run services logs read SERVICE_NAME --region=us-central1 --limit=50
```

**Update Domain Mapping:**
```bash
gcloud run services update SERVICE_NAME \
  --region=us-central1 \
  --add-custom-domain=yourdomain.com
```

---

## 🎯 **Next Steps:**

1. **Wait for current deployment to finish** (~10 min)
2. **Test new services** (verify they work)
3. **Update DNS** (point to new services)
4. **Monitor** (24-48 hours)
5. **Clean up old services**

---

**Status:** 🔄 **MIGRATION IN PROGRESS**  
**Current:** Deploying new services via CI/CD  
**Next:** Test and remap DNS

---

*Your app will be fully CI/CD managed soon!* 🚀✨
