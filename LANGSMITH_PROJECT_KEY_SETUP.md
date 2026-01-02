# ✅ Project-Scoped API Key Setup - Quick Guide

## What You Need to Do

### 1. Create Project API Key (In Browser)

The LangSmith page is now open. Follow these steps:

1. **Find Your Project**:
   - Look for "NexusAI" in your projects list
   - Click on it

2. **Open Settings**:
   - Click the **⚙️ Settings** icon (usually top-right)
   - Or look for "Settings" in the menu

3. **Go to API Keys**:
   - Click on **"API Keys"** tab
   - Click **"Create API Key"** or **"+ New API Key"**

4. **Choose Project Key**:
   - ⚠️ **Important**: Select **"Project API Key"** (NOT Organization)
   - Name it: `NexusAI-Development`
   - Click **Create**

5. **Copy the Key**:
   - Copy the entire key (starts with `lsv2_pt_...`)
   - ⚠️ Save it immediately! You can't view it again

---

### 2. Update Your .env File

Create or edit the file: `c:\Study\GenAI\Project\NexusAI\.env`

**Copy this template and fill in your keys**:

```bash
# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# LangSmith Configuration - PROJECT-SCOPED KEY
LANGSMITH_API_KEY=lsv2_pt_PASTE_YOUR_NEW_KEY_HERE
LANGSMITH_PROJECT=NexusAI
```

**Important Notes**:
- ✅ No `LANGSMITH_WORKSPACE_ID` needed!
- ✅ Much simpler than organization keys
- ✅ Works perfectly for single-project monitoring

---

### 3. Test the Setup

Run this command:

```bash
python test_langsmith_setup.py
```

**Expected Output**:
```
✅ LANGSMITH_API_KEY is set
   Key: lsv2_pt_ab...xyz
✅ LANGSMITH_PROJECT: NexusAI
ℹ️  LANGSMITH_WORKSPACE_ID is NOT set (optional, needed for org-scoped API keys)
✅ GEMINI_API_KEY is set

============================================================
Testing LangSmith Connection
============================================================
✅ Successfully connected to LangSmith
   Found 1 project(s)

============================================================
Summary
============================================================
✅ All tests passed! LangSmith is ready to use.
```

---

## Troubleshooting

### If you can't find "API Keys" in Settings:

Try this alternative path:
1. Go to https://smith.langchain.com/settings
2. Look for "API Keys" in the left sidebar
3. Click "Create API Key"
4. Choose your NexusAI project from the dropdown
5. Create the key

### If the test still fails:

1. **Check .env file location**: Must be in `c:\Study\GenAI\Project\NexusAI\.env`
2. **Check for spaces**: No spaces around `=` sign
3. **Restart terminal**: Close and reopen your terminal to reload environment variables

---

## What's Different from Organization Keys?

| Feature | Organization Key | Project Key |
|---------|------------------|-------------|
| Setup | Complex (needs workspace ID) | Simple |
| Permissions | All projects | Single project only |
| Reliability | Can have permission issues | Very reliable |
| Best for | Multi-project deployments | Single project (like NexusAI) |

---

## Next Steps After Setup

Once the test passes:

1. ✅ LangSmith tracing will work automatically
2. ✅ All your services (ImageGeneration, Chat, Director, etc.) will send traces
3. ✅ View traces at: https://smith.langchain.com/
4. ✅ Use analytics API: `/analytics/token-usage`
5. ✅ Open analytics dashboard: `frontend/analytics_dashboard.html`

---

**Time to Complete**: ~5 minutes  
**Difficulty**: Easy  
**Status**: Waiting for you to create the API key

---

**Once you have the key, just:**
1. Paste it in your `.env` file
2. Run `python test_langsmith_setup.py`
3. You're done! 🎉
