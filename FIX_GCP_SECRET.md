# 🔑 URGENT: Fix GCP_SA_KEY Secret

**Error:** `failed to parse service account key JSON credentials: expected double-quoted property name in JSON at position 1990`

**Status:** ❌ **INVALID JSON IN SECRET**  
**Action Required:** Re-add the `GCP_SA_KEY` secret with correct JSON

---

## 🐛 **Problem**

The `GCP_SA_KEY` secret in GitHub contains invalid JSON. The error at "position 1990" suggests:
- JSON was corrupted during copy/paste
- Extra characters were added
- Line breaks were inserted incorrectly
- The JSON is incomplete

---

## ✅ **Solution: Re-add the Secret**

### **Step 1: Get Your Service Account Key**

**Option A: If you have the file locally**
```powershell
# In PowerShell, navigate to where your key file is
Get-Content serviceAccountKey.json -Raw | Set-Clipboard
```
This copies the ENTIRE JSON to your clipboard.

**Option B: Download from Google Cloud Console**
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=gen-lang-client-0250626520
2. Find your service account (e.g., `github-actions@...`)
3. Click on it → **Keys** tab
4. If no key exists, click **Add Key** → **Create new key** → **JSON**
5. Download the JSON file
6. Open it in a text editor and copy ALL content

---

### **Step 2: Verify the JSON is Valid**

Before adding to GitHub, verify the JSON:

**Method 1: Use Python**
```powershell
# Save this as verify_json.py
python -c "import json; json.load(open('serviceAccountKey.json')); print('✅ JSON is valid')"
```

**Method 2: Use Online Validator**
- Go to: https://jsonlint.com/
- Paste your JSON
- Click "Validate JSON"
- Should show "Valid JSON"

**The JSON should look like this:**
```json
{
  "type": "service_account",
  "project_id": "gen-lang-client-0250626520",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@gen-lang-client-0250626520.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Important:**
- Must start with `{` and end with `}`
- All property names must be in double quotes: `"type":`
- The `private_key` will have `\n` characters (this is correct!)
- No trailing commas
- No comments

---

### **Step 3: Delete the Old Secret**

1. Go to: https://github.com/DKMMEHER/NexusAI/settings/secrets/actions
2. Find `GCP_SA_KEY`
3. Click **Remove** or **Delete**
4. Confirm deletion

---

### **Step 4: Add the Correct Secret**

1. Still on: https://github.com/DKMMEHER/NexusAI/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `GCP_SA_KEY` (EXACTLY this, case-sensitive)
4. **Value:** Paste the ENTIRE JSON content
   - **DO NOT** add extra spaces
   - **DO NOT** add line breaks
   - **DO NOT** modify the JSON in any way
   - Just paste exactly what you copied
5. Click **"Add secret"**

---

### **Step 5: Verify the Secret**

After adding:
1. You should see `GCP_SA_KEY` in the list
2. It will show "Updated X seconds ago"
3. You won't be able to see the value (GitHub hides it for security)

---

### **Step 6: Trigger a New Workflow Run**

**Option A: Re-run the Failed Workflow**
1. Go to: https://github.com/DKMMEHER/NexusAI/actions
2. Click on the failed run
3. Click **"Re-run all jobs"**

**Option B: Push a Small Change**
```powershell
# Make a small change
echo "# Secret fixed" >> README.md
git add README.md
git commit -m "chore: Trigger workflow after fixing GCP_SA_KEY secret"
git push origin main
```

---

## 🔍 **Common Mistakes to Avoid**

### ❌ **DON'T:**
1. **Don't copy from a text editor that adds formatting**
   - Use Notepad, VS Code, or `Get-Content` command
   
2. **Don't manually edit the JSON**
   - Use the file exactly as downloaded from Google Cloud
   
3. **Don't add extra line breaks**
   - The `\n` in `private_key` is correct - don't change it!
   
4. **Don't remove the quotes around property names**
   - `"type":` is correct, `type:` is wrong
   
5. **Don't add trailing commas**
   - `"value": "123",` at the end of an object is wrong

### ✅ **DO:**
1. **Copy the entire file content**
   - From `{` to `}` including everything
   
2. **Verify JSON is valid before adding**
   - Use `python -c "import json; json.load(open('file.json'))"`
   
3. **Use the exact file from Google Cloud**
   - Don't modify it in any way

---

## 🧪 **Test Your JSON Locally**

Create a test script to verify your JSON:

```python
# save as test_json.py
import json

try:
    with open('serviceAccountKey.json', 'r') as f:
        data = json.load(f)
    
    # Check required fields
    required_fields = ['type', 'project_id', 'private_key', 'client_email']
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing field: {field}")
        else:
            print(f"✅ Found field: {field}")
    
    print("\n✅ JSON is valid and has all required fields!")
    print(f"Project ID: {data['project_id']}")
    print(f"Service Account: {data['client_email']}")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON Error: {e}")
    print(f"Position: {e.pos}")
except FileNotFoundError:
    print("❌ File not found: serviceAccountKey.json")
```

Run it:
```powershell
python test_json.py
```

---

## 📋 **Quick Checklist**

- [ ] Located your `serviceAccountKey.json` file
- [ ] Verified JSON is valid (using Python or online validator)
- [ ] Deleted old `GCP_SA_KEY` secret from GitHub
- [ ] Added new `GCP_SA_KEY` secret with correct JSON
- [ ] Verified secret appears in GitHub secrets list
- [ ] Triggered a new workflow run
- [ ] Monitored the workflow to ensure it passes

---

## 🆘 **If You Don't Have the Service Account Key**

If you've lost the original key file:

1. **Create a New Key:**
   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=gen-lang-client-0250626520
   - Click on your service account
   - Go to **Keys** tab
   - Click **Add Key** → **Create new key**
   - Choose **JSON**
   - Download the file
   - Use this new file

2. **Delete Old Keys (Optional):**
   - In the Keys tab, you can delete old unused keys
   - This is good security practice

---

## 📞 **Quick Links**

- **GitHub Secrets:** https://github.com/DKMMEHER/NexusAI/settings/secrets/actions
- **Service Accounts:** https://console.cloud.google.com/iam-admin/serviceaccounts?project=gen-lang-client-0250626520
- **GitHub Actions:** https://github.com/DKMMEHER/NexusAI/actions
- **JSON Validator:** https://jsonlint.com/

---

## 🎯 **Expected Result**

After fixing the secret and re-running:

```
✅ Authenticate to Google Cloud     Success
✅ Set up Cloud SDK                  Success
✅ Configure Docker                  Success
✅ Build and Push Docker Image       Success
```

---

**Status:** 🔧 **ACTION REQUIRED**  
**Next Step:** Fix the `GCP_SA_KEY` secret in GitHub  
**Time Required:** ~5 minutes

---

*Once the secret is fixed, the build will proceed successfully!* ✅
