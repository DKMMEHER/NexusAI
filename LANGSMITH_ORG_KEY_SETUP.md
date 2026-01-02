# LangSmith Organization-Scoped API Key Setup

## Issue: "403 Forbidden - org-scoped API key requires workspace specification"

If you see this error:
```
Failed to connect to LangSmith: HTTPError('403 Client Error: Forbidden for url: https://api.smith.langchain.com/sessions?limit=1&offset=0', '{"detail":"This API key is org-scoped and requires workspace specification. Please provide \'X-Tenant-ID\' header."}')
```

This means your LangSmith API key is **organization-scoped** and requires a workspace ID.

---

## Solution: Add Workspace ID to .env

### Step 1: Find Your Workspace ID

1. Go to https://smith.langchain.com/
2. Navigate to your project
3. Look at the URL in your browser

The URL will look like:
```
https://smith.langchain.com/o/YOUR_WORKSPACE_ID/projects/p/YOUR_PROJECT
```

**Copy the `YOUR_WORKSPACE_ID` part** (the value after `/o/`)

### Step 2: Add to .env File

Add this line to your `.env` file:

```bash
LANGSMITH_WORKSPACE_ID=YOUR_WORKSPACE_ID
```

**Example:**
```bash
LANGSMITH_API_KEY=lsv2_pt_abc123def456...
LANGSMITH_PROJECT=NexusAI
LANGSMITH_WORKSPACE_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Step 3: Verify Setup

Run the verification script again:

```bash
python test_langsmith_setup.py
```

You should now see:
```
✅ LANGSMITH_WORKSPACE_ID is set: a1b2c3d4...
✅ Successfully connected to LangSmith
```

---

## Alternative: Use Project-Scoped API Key

If you don't want to use organization-scoped keys, you can create a **project-scoped API key** instead:

1. Go to https://smith.langchain.com/
2. Navigate to your specific project
3. Click **Settings** → **API Keys**
4. Create a new **Project API Key** (not Organization API Key)
5. Use this key in your `.env` file

Project-scoped keys don't require a tenant ID.

---

## Understanding API Key Types

### Organization-Scoped Keys
- ✅ Access to all projects in the organization
- ✅ Can create new projects
- ❌ Requires `LANGSMITH_WORKSPACE_ID`
- **Use case**: Multi-project deployments, CI/CD

### Project-Scoped Keys
- ✅ Access to a specific project only
- ✅ No tenant ID required
- ❌ Cannot access other projects
- **Use case**: Single project, simpler setup

---

## Troubleshooting

### Issue: "Tenant ID not found in URL"

If you can't find the tenant ID in the URL, try:

1. Click on your organization name in the top-left corner
2. Go to **Organization Settings**
3. Look for **Organization ID** or **Workspace ID**
4. Copy that value

### Issue: "Still getting 403 error"

1. Double-check the tenant ID is correct
2. Make sure there are no extra spaces in `.env`
3. Restart your application to reload environment variables
4. Try creating a project-scoped API key instead

### Issue: "Environment variable not loading"

1. Make sure `.env` file is in the project root
2. Verify `python-dotenv` is installed: `pip install python-dotenv`
3. Check that your code calls `load_dotenv()` before accessing env vars
4. Try printing the value: `print(os.getenv("LANGSMITH_WORKSPACE_ID"))`

---

## Updated Configuration

Your complete `.env` file should look like:

```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud (optional)
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_LOCATION=us-central1

# LangSmith Configuration
LANGSMITH_API_KEY=lsv2_pt_your_api_key_here
LANGSMITH_PROJECT=NexusAI
LANGSMITH_WORKSPACE_ID=your_workspace_id_here  # For org-scoped keys
```

---

## How It Works

When you set `LANGSMITH_WORKSPACE_ID`, the code automatically uses it for authentication:

```python
# In langsmith_config.py
if workspace_id:
    os.environ["LANGSMITH_WORKSPACE_ID"] = workspace_id

# LangSmith SDK automatically uses this
client = Client(api_key=api_key)
```

---

## Need More Help?

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **LangSmith Support**: https://smith.langchain.com/support
- **Check Setup**: Run `python test_langsmith_setup.py`

---

**Last Updated**: 2026-01-02  
**Issue**: Organization-scoped API keys  
**Status**: ✅ Resolved
