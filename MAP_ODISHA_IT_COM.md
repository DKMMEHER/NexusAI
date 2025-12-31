# 🌐 Map odisha.it.com to New Deployment

**Domain:** odisha.it.com  
**New Service:** director-962267416185.asia-south1.run.app  
**Region:** asia-south1

---

## 🚀 **Step-by-Step Instructions:**

### **Step 1: Check Current Domain Mapping**

```bash
gcloud run domain-mappings list --region=asia-south1 --project=gen-lang-client-0250626520
```

This will show if `odisha.it.com` is currently mapped to any service.

---

### **Step 2: Remove Old Mapping (If Exists)**

```bash
gcloud run domain-mappings delete \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --project=gen-lang-client-0250626520
```

**Note:** If it says "not found", that's okay! It means no old mapping exists.

---

### **Step 3: Map to New Director Service**

```bash
gcloud run domain-mappings create \
  --service=director \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --project=gen-lang-client-0250626520
```

**This command will:**
- ✅ Map `odisha.it.com` to the Director service
- ✅ Provision SSL certificate automatically
- ✅ Show you DNS records to add

---

### **Step 4: Update DNS Records**

The command will output DNS records. You'll see something like:

```
Please add the following DNS records to your domain's DNS configuration:

Type: A
Name: odisha.it.com
Value: 216.239.32.21

Type: A
Name: odisha.it.com
Value: 216.239.34.21

Type: A
Name: odisha.it.com
Value: 216.239.36.21

Type: A
Name: odisha.it.com
Value: 216.239.38.21

Type: AAAA
Name: odisha.it.com
Value: 2001:4860:4802:32::15

Type: AAAA
Name: odisha.it.com
Value: 2001:4860:4802:34::15

Type: AAAA
Name: odisha.it.com
Value: 2001:4860:4802:36::15

Type: AAAA
Name: odisha.it.com
Value: 2001:4860:4802:38::15
```

---

### **Step 5: Add DNS Records in Your DNS Provider**

**Go to your DNS provider** (where you manage `it.com`):

1. **Find DNS Management** section
2. **Add subdomain:** `odisha`
3. **Add A records** (4 records from Step 4)
4. **Add AAAA records** (4 records from Step 4)
5. **Save changes**

**Example for Cloudflare:**
```
Type: A
Name: odisha
Content: 216.239.32.21
TTL: Auto
Proxy: OFF (DNS only)
```

Repeat for all 8 records (4 A + 4 AAAA).

---

### **Step 6: Verify Domain Mapping**

```bash
gcloud run domain-mappings describe \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --project=gen-lang-client-0250626520
```

**Look for:**
```
certificateStatus: ACTIVE
resourceRecords:
  - rrdata: 216.239.32.21
    type: A
```

---

### **Step 7: Wait for SSL Certificate**

**Time required:** 15-30 minutes

**Check status:**
```bash
# Every 5 minutes, run:
gcloud run domain-mappings describe \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --project=gen-lang-client-0250626520 \
  --format='value(status.conditions[0].message)'
```

**When you see:** "Ready to serve."  
**Your domain is ready!** ✅

---

### **Step 8: Test Your Domain**

```bash
# Test DNS resolution
nslookup odisha.it.com

# Test HTTP
curl -I http://odisha.it.com

# Test HTTPS
curl -I https://odisha.it.com
```

**Then open in browser:**
```
https://odisha.it.com
```

Should load your React frontend! 🎉

---

## 📋 **Quick Command Summary:**

```bash
# 1. Check current mapping
gcloud run domain-mappings list --region=asia-south1

# 2. Delete old mapping (if exists)
gcloud run domain-mappings delete \
  --domain=odisha.it.com \
  --region=asia-south1

# 3. Create new mapping
gcloud run domain-mappings create \
  --service=director \
  --domain=odisha.it.com \
  --region=asia-south1

# 4. Check status
gcloud run domain-mappings describe \
  --domain=odisha.it.com \
  --region=asia-south1

# 5. Test
curl -I https://odisha.it.com
```

---

## 🔍 **Troubleshooting:**

### **Issue 1: "Domain already exists"**

**Solution:**
```bash
# Delete the old mapping first
gcloud run domain-mappings delete \
  --domain=odisha.it.com \
  --region=asia-south1
```

---

### **Issue 2: "SSL certificate pending"**

**Solution:** Wait 15-30 minutes. SSL provisioning takes time.

**Check status:**
```bash
gcloud run domain-mappings describe \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --format='value(status.conditions[0].message)'
```

---

### **Issue 3: "DNS not resolving"**

**Solution:**
```bash
# Clear DNS cache
ipconfig /flushdns

# Check DNS propagation
nslookup odisha.it.com

# Check globally: https://dnschecker.org
```

---

### **Issue 4: "Certificate error in browser"**

**Solution:** 
- Wait for SSL certificate to be provisioned (15-30 min)
- Make sure you're using `https://` not `http://`
- Clear browser cache or use incognito mode

---

## ⏰ **Timeline:**

```
Now:           Run Step 1-3 (5 min)
+5 min:        Update DNS records (5 min)
+10 min:       DNS propagation starts
+15-30 min:    SSL certificate provisioned
+30 min:       https://odisha.it.com works! 🎉
```

---

## ✅ **Success Checklist:**

- [ ] Old domain mapping deleted
- [ ] New domain mapping created
- [ ] DNS records updated in DNS provider
- [ ] DNS resolves to Google IPs
- [ ] SSL certificate status: ACTIVE
- [ ] https://odisha.it.com loads frontend
- [ ] All features work
- [ ] No SSL errors

---

## 🎯 **Next Steps After Domain Works:**

1. **Test all features** on `https://odisha.it.com`
2. **Update frontend config** (if needed) to use new domain
3. **Update any hardcoded URLs** in your code
4. **Share your app** with the world! 🌐

---

**Status:** 📋 **READY TO MAP DOMAIN**  
**Domain:** odisha.it.com  
**Service:** director (asia-south1)  
**Action:** Run the commands above!

---

*Your custom domain will be live in ~30 minutes!* 🚀✨
