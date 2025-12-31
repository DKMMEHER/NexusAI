# ⚠️ Domain Verification Required

**Issue:** `odisha.it.com` needs to be verified before mapping to Cloud Run  
**Current:** Only `dhirendrameher.blogspot.com` is verified  
**Solution:** Verify domain ownership in Google Search Console

---

## 🔐 **Step 1: Verify Domain Ownership**

### **Option A: Google Search Console (Recommended)**

1. **Go to Google Search Console:**
   - https://search.google.com/search-console

2. **Add Property:**
   - Click "Add Property"
   - Select "Domain" (not URL prefix)
   - Enter: `it.com` (the root domain)

3. **Verify via DNS:**
   - Google will give you a TXT record
   - Add it to your DNS provider
   - Click "Verify"

**Example TXT record:**
```
Type: TXT
Name: @ (or it.com)
Value: google-site-verification=xxxxxxxxxxxxx
TTL: 3600
```

---

### **Option B: Verify via Cloud Run (Alternative)**

```bash
gcloud domains verify odisha.it.com
```

This will guide you through the verification process.

---

## 🌐 **Step 2: Update DNS Provider**

**Go to your DNS provider** (where you manage `it.com`):

### **Add Verification TXT Record:**

1. Log in to DNS provider
2. Go to DNS management for `it.com`
3. Add TXT record from Google Search Console
4. Save changes
5. Wait 5-10 minutes
6. Return to Search Console and click "Verify"

---

## ✅ **Step 3: After Verification**

Once `it.com` (or `odisha.it.com`) is verified, run:

```bash
gcloud beta run domain-mappings create \
  --service=director \
  --domain=odisha.it.com \
  --region=asia-south1 \
  --project=gen-lang-client-0250626520
```

---

## 🔄 **Alternative: Use Subdomain of Verified Domain**

**If you have `dhirendrameher.blogspot.com` verified:**

You could use a subdomain like:
- `nexusai.dhirendrameher.blogspot.com`
- Or get a new domain and verify it

---

## 📋 **Quick Steps Summary:**

```
1. Go to: https://search.google.com/search-console
2. Add property: it.com
3. Get TXT record
4. Add TXT record to DNS
5. Wait 5-10 minutes
6. Click "Verify" in Search Console
7. Run domain mapping command again
```

---

## 🎯 **Verification Status:**

**Currently Verified:**
```
✅ dhirendrameher.blogspot.com
```

**Need to Verify:**
```
⏳ it.com (or odisha.it.com)
```

---

## 📞 **Detailed Verification Guide:**

### **For it.com (Root Domain):**

1. **Google Search Console:**
   - https://search.google.com/search-console
   - Add property → Domain
   - Enter: `it.com`

2. **Get TXT Record:**
   ```
   Type: TXT
   Name: @
   Value: google-site-verification=ABC123...
   ```

3. **Add to DNS Provider:**
   - Log in to DNS provider
   - Add TXT record
   - Save

4. **Verify:**
   - Return to Search Console
   - Click "Verify"
   - Wait for confirmation

5. **Then Map Domain:**
   ```bash
   gcloud beta run domain-mappings create \
     --service=director \
     --domain=odisha.it.com \
     --region=asia-south1
   ```

---

## ⏰ **Timeline:**

```
Now:           Start verification (5 min)
+5 min:        Add TXT record to DNS (5 min)
+10 min:       DNS propagation (5-10 min)
+15 min:       Verify in Search Console (2 min)
+20 min:       Create domain mapping (2 min)
+30-45 min:    SSL certificate + DNS propagation
+1 hour:       https://odisha.it.com works! 🎉
```

---

## 🔍 **Troubleshooting:**

### **Issue: "Domain not verified"**

**Solution:**
1. Check TXT record is added correctly
2. Wait 10-15 minutes for DNS propagation
3. Try verification again
4. Use `nslookup -type=TXT it.com` to verify TXT record

---

### **Issue: "Don't have access to DNS"**

**Solution:**
- Contact domain administrator
- Or use a different domain you control
- Or use Cloud Run default URL for now

---

## 💡 **Alternative Solutions:**

### **Option 1: Use Cloud Run Default URL**

**For now, use:**
```
https://director-962267416185.asia-south1.run.app
```

**Pros:**
- Works immediately
- No verification needed
- Free SSL

**Cons:**
- Long URL
- Not branded

---

### **Option 2: Get a New Domain**

**Buy a domain you control:**
- Namecheap: ~$10/year
- Google Domains: ~$12/year
- Cloudflare: ~$10/year

**Then:**
1. Verify ownership
2. Map to Cloud Run
3. Done!

---

### **Option 3: Use Subdomain of Verified Domain**

**If you control `dhirendrameher.blogspot.com`:**

You could potentially use:
```
nexusai.dhirendrameher.com (if you own dhirendrameher.com)
```

---

## 📊 **What You Need:**

**To map `odisha.it.com`, you need:**

1. ✅ Access to `it.com` DNS settings
2. ✅ Ability to add TXT record
3. ✅ Verify domain in Google Search Console
4. ✅ Then map to Cloud Run

**OR:**

1. ✅ Use Cloud Run default URL (works now!)
2. ✅ Get custom domain later

---

## 🎯 **Recommended Action:**

### **For Now:**

**Use the Cloud Run URL:**
```
https://director-962267416185.asia-south1.run.app
```

**This works immediately and has:**
- ✅ Free SSL certificate
- ✅ Global CDN
- ✅ Auto-scaling
- ✅ All features working

---

### **Later:**

**Verify and map custom domain:**
1. Verify `it.com` in Search Console
2. Map `odisha.it.com` to Cloud Run
3. Update DNS records
4. Done!

---

**Status:** ⚠️ **DOMAIN VERIFICATION REQUIRED**  
**Action:** Verify `it.com` in Google Search Console  
**Alternative:** Use Cloud Run URL for now

---

*Once domain is verified, mapping takes only 5 minutes!* 🌐✨
