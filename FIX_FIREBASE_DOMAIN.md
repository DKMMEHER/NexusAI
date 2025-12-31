# 🔧 Fix: Firebase Unauthorized Domain Error

**Error:** `Firebase: Error (auth/unauthorized-domain)`  
**Cause:** Cloud Run URL not authorized in Firebase  
**Solution:** Add domain to Firebase Console (5 minutes)

---

## ✅ **Quick Fix:**

### **Step 1: Go to Firebase Console**

Open this link:
```
https://console.firebase.google.com/project/gen-lang-client-0250626520/authentication/settings
```

Or manually:
1. Go to: https://console.firebase.google.com
2. Select project: `gen-lang-client-0250626520`
3. Click "Authentication" (left sidebar)
4. Click "Settings" tab
5. Scroll to "Authorized domains"

---

### **Step 2: Add Cloud Run Domain**

**Click "Add domain"** and add:
```
director-962267416185.asia-south1.run.app
```

**Also add (if using custom domain later):**
```
odisha.it.com
```

---

### **Step 3: Save**

Click "Add" or "Save"

**Wait:** 1-2 minutes for changes to propagate

---

### **Step 4: Test**

1. Refresh your browser
2. Go to: `https://director-962267416185.asia-south1.run.app`
3. Click "Login with Google"
4. Should work now! ✅

---

## 📋 **Detailed Steps with Screenshots:**

### **1. Open Firebase Console**
```
https://console.firebase.google.com/project/gen-lang-client-0250626520/authentication/settings
```

### **2. Find "Authorized domains" Section**

You should see a list like:
```
✅ localhost
✅ gen-lang-client-0250626520.firebaseapp.com
✅ gen-lang-client-0250626520.web.app
❌ director-962267416185.asia-south1.run.app (MISSING!)
```

### **3. Click "Add domain"**

A dialog will appear.

### **4. Enter Domain**
```
director-962267416185.asia-south1.run.app
```

**Important:** 
- ✅ Include: `director-962267416185.asia-south1.run.app`
- ❌ Don't include: `https://`
- ❌ Don't include: trailing `/`

### **5. Click "Add"**

Domain will be added to the list.

### **6. Verify**

You should now see:
```
✅ localhost
✅ gen-lang-client-0250626520.firebaseapp.com
✅ gen-lang-client-0250626520.web.app
✅ director-962267416185.asia-south1.run.app (NEW!)
```

---

## 🎯 **What This Does:**

Firebase Authentication only allows login from **authorized domains** for security.

**Before:**
- Only `localhost` and Firebase domains authorized
- Cloud Run domain NOT authorized
- Login fails with `auth/unauthorized-domain`

**After:**
- Cloud Run domain added to authorized list
- Firebase allows login from Cloud Run URL
- Login works! ✅

---

## 🔐 **Security Note:**

This is a **security feature**, not a bug!

Firebase blocks login attempts from unauthorized domains to prevent:
- Phishing attacks
- Unauthorized use of your Firebase project
- Domain hijacking

**Always add only domains you control!**

---

## 📊 **Domains to Add:**

### **For Development:**
```
✅ localhost (already added)
```

### **For Production (Cloud Run):**
```
✅ director-962267416185.asia-south1.run.app (add this!)
```

### **For Custom Domain (Later):**
```
✅ odisha.it.com (add when you set up custom domain)
```

---

## ⏰ **Timeline:**

```
Now:           Add domain to Firebase (2 min)
+2 min:        Save changes
+3 min:        Changes propagate
+5 min:        Test login - should work! ✅
```

---

## 🎯 **After Adding Domain:**

### **Test Login:**

1. **Refresh browser:**
   ```
   Ctrl + F5 (hard refresh)
   ```

2. **Go to app:**
   ```
   https://director-962267416185.asia-south1.run.app
   ```

3. **Click "Login with Google"**

4. **Should see:**
   - Google login popup
   - Select account
   - Authenticate
   - Redirect to dashboard ✅

---

## 🔍 **If Still Not Working:**

### **Check 1: Domain Spelling**

Make sure you added:
```
director-962267416185.asia-south1.run.app
```

**NOT:**
```
❌ https://director-962267416185.asia-south1.run.app
❌ director-962267416185.asia-south1.run.app/
❌ director-962267416185.asia-south1.run.app/login
```

### **Check 2: Wait a Bit**

Firebase changes can take 1-2 minutes to propagate.

**Solution:** Wait 2 minutes, then try again.

### **Check 3: Clear Browser Cache**

```
1. Press Ctrl + Shift + Delete
2. Clear cached images and files
3. Close browser
4. Reopen and try again
```

### **Check 4: Try Incognito Mode**

```
1. Open incognito/private window
2. Go to app
3. Try login
```

---

## 📞 **Quick Reference:**

### **Firebase Console:**
```
https://console.firebase.google.com/project/gen-lang-client-0250626520/authentication/settings
```

### **Domain to Add:**
```
director-962267416185.asia-south1.run.app
```

### **Where to Add:**
```
Authentication → Settings → Authorized domains → Add domain
```

---

## ✅ **Success Criteria:**

**You'll know it worked when:**

1. ✅ No more `auth/unauthorized-domain` error
2. ✅ Google login popup opens
3. ✅ Can select Google account
4. ✅ Redirects to dashboard after login
5. ✅ Can use all features

---

## 🎊 **After Login Works:**

You'll be able to:
- ✅ Generate images
- ✅ Create videos
- ✅ Use chat
- ✅ Summarize documents
- ✅ Get YouTube transcripts
- ✅ Create movies with Director

**All with your own user account!**

---

## 💡 **Pro Tip:**

**Add all domains now:**

```
✅ localhost (for local development)
✅ director-962267416185.asia-south1.run.app (for Cloud Run)
✅ odisha.it.com (for custom domain - when ready)
```

This way you won't have this issue again!

---

## 🎯 **Summary:**

**Problem:** Firebase blocking login from Cloud Run URL  
**Solution:** Add Cloud Run domain to Firebase authorized domains  
**Time:** 5 minutes  
**Difficulty:** Easy

---

**Status:** 🔧 **EASY FIX**  
**Action:** Add domain to Firebase Console  
**ETA:** 5 minutes to working login!

---

*This is a quick fix! Just add the domain and you're good to go!* 🚀✨
