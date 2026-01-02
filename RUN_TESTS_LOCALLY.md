# 🧪 Running Tests Locally

**Purpose:** Test before pushing to save CI/CD time and quota

---

## 📋 **Quick Commands:**

### **Run All Tests:**
```bash
pytest tests/ -v
```

### **Run Unit Tests Only:**
```bash
pytest tests/unit/ -v
```

### **Run Integration Tests Only:**
```bash
pytest tests/integration/ -v
```

### **Run Specific Test File:**
```bash
pytest tests/unit/test_youtube_transcript_unit.py -v
```

### **Run with Coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
```

---

## 🚀 **Setup (First Time Only):**

### **1. Install Dependencies:**
```bash
pip install -r requirements.txt
pip install pytest pytest-mock pytest-cov
```

### **2. Set Environment Variables:**
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-key-here"
$env:GOOGLE_CLOUD_PROJECT="gen-lang-client-0250626520"
$env:YOUTUBE_API_KEY="your-youtube-key-here"

# Or create .env file
```

---

## 📊 **Test Structure:**

```
tests/
├── unit/                           # Fast, isolated tests
│   ├── test_image_generation_unit.py
│   ├── test_video_generation_unit.py
│   ├── test_chat_unit.py
│   ├── test_documents_unit.py
│   ├── test_youtube_transcript_unit.py
│   └── test_director_unit.py
│
└── integration/                    # Slower, end-to-end tests
    ├── test_image_generation_integration.py
    ├── test_video_generation_integration.py
    ├── test_chat_integration.py
    ├── test_documents_integration.py
    ├── test_youtube_integration.py
    └── test_director_integration.py
```

---

## ⚡ **Quick Test Workflow:**

### **Before Committing:**

```bash
# 1. Run unit tests (fast - ~30 seconds)
pytest tests/unit/ -v

# 2. If unit tests pass, run integration tests (~2-3 minutes)
pytest tests/integration/ -v

# 3. If all pass, commit and push
git add .
git commit -m "your message"
git push origin main
```

---

## 🎯 **Test Output:**

### **Success:**
```
tests/unit/test_youtube_transcript_unit.py::test_extract_transcript_summary_success PASSED
tests/unit/test_youtube_transcript_unit.py::test_invalid_url_format PASSED
tests/unit/test_youtube_transcript_unit.py::test_transcript_api_failure PASSED
tests/unit/test_youtube_transcript_unit.py::test_health_check_explicit PASSED

====== 4 passed in 2.5s ======
```

### **Failure:**
```
tests/unit/test_youtube_transcript_unit.py::test_invalid_url_format FAILED

FAILED tests/unit/test_youtube_transcript_unit.py::test_invalid_url_format
assert 500 == 400
```

---

## 💡 **Pro Tips:**

### **1. Run Tests in Watch Mode:**
```bash
pytest-watch tests/unit/
```
Auto-runs tests when files change

### **2. Run Only Failed Tests:**
```bash
pytest --lf  # Last failed
```

### **3. Stop on First Failure:**
```bash
pytest -x
```

### **4. Show Print Statements:**
```bash
pytest -s
```

### **5. Run Specific Test:**
```bash
pytest tests/unit/test_youtube_transcript_unit.py::test_invalid_url_format -v
```

---

## 🔧 **Common Issues:**

### **Issue 1: Module Not Found**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### **Issue 2: Import Errors**
```bash
# Solution: Run from project root
cd c:\Study\GenAI\Project\NexusAI
pytest tests/
```

### **Issue 3: Environment Variables Missing**
```bash
# Solution: Set env vars or create .env file
$env:GEMINI_API_KEY="your-key"
```

---

## 📊 **Test Coverage:**

### **Generate Coverage Report:**
```bash
pytest tests/ --cov=. --cov-report=html
```

### **View Report:**
```
Open: htmlcov/index.html
```

---

## ⏰ **Time Comparison:**

### **Local Testing:**
```
Unit Tests:        ~30 seconds
Integration Tests: ~2-3 minutes
Total:            ~3-4 minutes
```

### **CI/CD Testing:**
```
Setup:            ~2 minutes
Unit Tests:       ~1 minute
Integration:      ~3 minutes
Total:           ~6-8 minutes
```

**Local is faster!** ✅

---

## 🎯 **Best Practice Workflow:**

```bash
# 1. Make changes to code
# 2. Run affected unit tests
pytest tests/unit/test_youtube_transcript_unit.py -v

# 3. If pass, run all unit tests
pytest tests/unit/ -v

# 4. If pass, run integration tests
pytest tests/integration/ -v

# 5. If all pass, commit and push
git add .
git commit -m "feat: your feature"
git push origin main
```

---

## 📋 **Quick Reference:**

```bash
# All tests
pytest tests/ -v

# Unit only (fast)
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# Specific file
pytest tests/unit/test_youtube_transcript_unit.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Stop on first fail
pytest -x

# Show prints
pytest -s

# Last failed only
pytest --lf
```

---

## 🎊 **Benefits of Local Testing:**

```
✅ Faster feedback (30 sec vs 6 min)
✅ Save CI/CD quota
✅ Iterate quickly
✅ Debug easier
✅ No waiting for GitHub Actions
```

---

**Next time, run `pytest tests/unit/ -v` before pushing!** 🚀✨
