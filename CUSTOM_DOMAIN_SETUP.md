# 🌐 Map Custom Domain to New Deployment

**Goal:** Point your custom domain to the new Director service  
**Old URL:** Your old nexusai deployment  
**New URL:** https://director-962267416185.asia-south1.run.app

---

## 📋 **Two Methods to Choose From:**

### **Method 1: Cloud Run Domain Mapping (Recommended)**
- ✅ Automatic SSL certificate
- ✅ Managed by Google
- ✅ Easy to set up

### **Method 2: DNS Provider Update (Manual)**
- ✅ More control
- ✅ Works with any DNS provider
- ✅ Faster propagation

---

## 🚀 **Method 1: Cloud Run Domain Mapping (Easiest)**

### **Step 1: Remove Old Domain Mapping**

First, check what domain is currently mapped:

```bash
gcloud run domain-mappings list --region=asia-south1
```

If you see your domain mapped to the old service, delete it:

```bash
# Replace yourdomain.com with your actual domain
gcloud run domain-mappings delete \
  --domain=yourdomain.com \
  --region=asia-south1
```

---

### **Step 2: Add Domain to Director Service**

```bash
# Replace yourdomain.com with your actual domain
gcloud run services add-iam-policy-binding director \
  --region=asia-south1 \
  --member="allUsers" \
  --role="roles/run.invoker"

gcloud run domain-mappings create \
  --service=director \
  --domain=yourdomain.com \
  --region=asia-south1
```

---

### **Step 3: Verify DNS Records**

The command will show you DNS records to add. It will look like:

```
Please add the following DNS records:

Type: A
Name: yourdomain.com
Value: 216.239.32.21

Type: A
Name: yourdomain.com
Value: 216.239.34.21

Type: A
Name: yourdomain.com
Value: 216.239.36.21

Type: A
Name: yourdomain.com
Value: 216.239.38.21

Type: AAAA
Name: yourdomain.com
Value: 2001:4860:4802:32::15

Type: AAAA
Name: yourdomain.com
Value: 2001:4860:4802:34::15

Type: AAAA
Name: yourdomain.com
Value: 2001:4860:4802:36::15

Type: AAAA
Name: yourdomain.com
Value: 2001:4860:4802:38::15
```

---

### **Step 4: Update DNS Provider**

Go to your DNS provider (Cloudflare, GoDaddy, Namecheap, etc.) and:

1. **Delete old records** pointing to the old service
2. **Add new A records** (from Step 3)
3. **Add new AAAA records** (from Step 3)

---

### **Step 5: Wait for Verification**

```bash
# Check status
gcloud run domain-mappings describe \
  --domain=yourdomain.com \
  --region=asia-south1
```

**Wait time:** 15-30 minutes for DNS propagation and SSL certificate

---

## 🔧 **Method 2: DNS Provider Update (Manual)**

### **Step 1: Get Current Domain Mapping**

Check what your domain currently points to:

```bash
nslookup yourdomain.com
```

---

### **Step 2: Update DNS Records**

**Option A: CNAME Record (Recommended)**

In your DNS provider, update the CNAME record:

```
Type: CNAME
Name: @ (or yourdomain.com)
Value: director-962267416185.asia-south1.run.app
TTL: 300 (5 minutes)
```

**Option B: A Records**

If CNAME doesn't work, use A records:

```
Type: A
Name: @ (or yourdomain.com)
Value: [Get IP from: ping director-962267416185.asia-south1.run.app]
```

---

### **Step 3: Verify Update**

```bash
# Check DNS propagation
nslookup yourdomain.com

# Test the domain
curl -I https://yourdomain.com
```

---

## 📊 **Common DNS Providers:**

### **Cloudflare:**

1. Log in to Cloudflare
2. Select your domain
3. Go to DNS → Records
4. Click "Edit" on existing record
5. Update value to: `director-962267416185.asia-south1.run.app`
6. Save

---

### **GoDaddy:**

1. Log in to GoDaddy
2. My Products → DNS
3. Click "Edit" on A or CNAME record
4. Update value to: `director-962267416185.asia-south1.run.app`
5. Save (TTL: 600 seconds)

---

### **Namecheap:**

1. Log in to Namecheap
2. Domain List → Manage
3. Advanced DNS
4. Edit existing record
5. Update value to: `director-962267416185.asia-south1.run.app`
6. Save

---

### **Google Domains:**

1. Log in to Google Domains
2. My domains → DNS
3. Custom records
4. Edit existing record
5. Update value to: `director-962267416185.asia-south1.run.app`
6. Save

---

## ✅ **Verification Steps:**

### **1. Check DNS Propagation:**

```bash
# Check if DNS updated
nslookup yourdomain.com

# Should show:
# Name: director-962267416185.asia-south1.run.app
```

---

### **2. Test HTTP/HTTPS:**

```bash
# Test HTTP
curl -I http://yourdomain.com

# Test HTTPS
curl -I https://yourdomain.com
```

---

### **3. Test in Browser:**

1. Open `https://yourdomain.com`
2. Should load your React frontend
3. SSL certificate should be valid (green lock)

---

## 🔍 **Troubleshooting:**

### **Issue 1: DNS Not Updating**

```bash
# Clear DNS cache (Windows)
ipconfig /flushdns

# Check propagation globally
# Visit: https://dnschecker.org
# Enter: yourdomain.com
```

**Solution:** Wait 5-30 minutes for propagation

---

### **Issue 2: SSL Certificate Error**

**Symptoms:** "Your connection is not private"

**Solution:**
```bash
# If using Cloud Run domain mapping, wait for SSL provisioning
gcloud run domain-mappings describe \
  --domain=yourdomain.com \
  --region=asia-south1

# Look for: certificateStatus: ACTIVE
```

**Wait time:** 15-30 minutes for SSL certificate

---

### **Issue 3: 404 Not Found**

**Symptoms:** Domain loads but shows 404

**Solution:**
```bash
# Verify service is running
gcloud run services describe director --region=asia-south1

# Check if domain mapping is correct
gcloud run domain-mappings list --region=asia-south1
```

---

### **Issue 4: Old App Still Loading**

**Symptoms:** Domain shows old app

**Solution:**
```bash
# Clear browser cache
# Or use incognito mode

# Verify DNS updated
nslookup yourdomain.com
```

---

## 📋 **Quick Command Reference:**

### **List Current Mappings:**
```bash
gcloud run domain-mappings list --region=asia-south1
```

### **Delete Old Mapping:**
```bash
gcloud run domain-mappings delete \
  --domain=yourdomain.com \
  --region=asia-south1
```

### **Create New Mapping:**
```bash
gcloud run domain-mappings create \
  --service=director \
  --domain=yourdomain.com \
  --region=asia-south1
```

### **Check Mapping Status:**
```bash
gcloud run domain-mappings describe \
  --domain=yourdomain.com \
  --region=asia-south1
```

---

## 🎯 **Recommended Approach:**

**For your situation (migrating from old app):**

### **Step-by-Step:**

1. **Test new deployment first:**
   ```
   https://director-962267416185.asia-south1.run.app
   ```

2. **Remove old domain mapping:**
   ```bash
   gcloud run domain-mappings delete \
     --domain=yourdomain.com \
     --region=asia-south1
   ```

3. **Add to new Director service:**
   ```bash
   gcloud run domain-mappings create \
     --service=director \
     --domain=yourdomain.com \
     --region=asia-south1
   ```

4. **Update DNS records** (if needed)

5. **Wait 15-30 minutes**

6. **Test:** `https://yourdomain.com`

---

## ⏰ **Timeline:**

```
Now:           Remove old mapping (2 min)
+2 min:        Create new mapping (2 min)
+5 min:        Update DNS (if needed) (5 min)
+15-30 min:    DNS propagation + SSL
+30 min:       Domain fully working! 🎉
```

---

## 🎊 **Success Criteria:**

### **You're successful when:**

1. ✅ `https://yourdomain.com` loads your React frontend
2. ✅ SSL certificate is valid (green lock)
3. ✅ All features work
4. ✅ No errors in browser console
5. ✅ Old app is no longer accessible

---

## 📞 **Need Help?**

**Check these:**
- DNS propagation: https://dnschecker.org
- SSL status: https://www.ssllabs.com/ssltest/
- Cloud Run console: https://console.cloud.google.com/run

---

**Status:** 📋 **READY TO MAP DOMAIN**  
**Action:** Follow Method 1 (Cloud Run Domain Mapping)  
**Time:** ~30 minutes total

---

*Your custom domain will soon point to your new CI/CD-managed deployment!* 🌐✨
