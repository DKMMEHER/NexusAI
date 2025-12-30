# 🔧 Complete Fix for test_document_summarization_integration.py

## All Indentation Issues Found:

### Issue 1: Lines 136-151 (test_summarize_with_different_models)
**Problem:** Code outside for loop, line 151 has extra indentation

### Issue 2: Lines 214-235 (test_database_integration)  
**Problem:** Code outside with block

### Issue 3: Lines 241-247 (test_concurrent_summarization_requests)
**Problem:** Incorrect indentation in make_request function

---

## COMPLETE FIXED CODE

Copy and paste these sections to replace the broken ones:

### Fix 1: Replace lines 136-151 with:

```python
        for model in models:
            fake_txt = io.BytesIO(f"Test document for model {model}".encode())
            
            response = client.post(
                "/summarize",
                files={"files": ("test.txt", fake_txt, "text/plain")},
                data={
                    "model": model,
                    "user_id": "test_user_123"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            print(f"✅ Model {model} works correctly")
```

### Fix 2: Replace lines 214-235 with:

```python
        with patch("DocumentsSummarization.backend.db") as mock_db:
            fake_txt = io.BytesIO(b"Database integration test document")
            
            response = client.post(
                "/summarize",
                files={"files": ("test.txt", fake_txt, "text/plain")},
                data={"user_id": "test_user_123"}
            )
            
            assert response.status_code == 200
            
            # Verify database save was called
            mock_db.save_job.assert_called_once()
            
            # Verify the saved data structure
            call_args = mock_db.save_job.call_args[0][0]
            assert "job_id" in call_args
            assert "user_id" in call_args
            assert call_args["user_id"] == "test_user_123"
            assert "type" in call_args
            
            print("✅ Database integration works correctly")
```

### Fix 3: Replace lines 241-247 with:

```python
        def make_request(i):
            fake_txt = io.BytesIO(f"Concurrent document {i} with content to summarize.".encode())
            return client.post(
                "/summarize",
                files={"files": (f"doc{i}.txt", fake_txt, "text/plain")},
                data={"user_id": f"user_{i}"}
            )
```

---

## OR: Use Find & Replace in VS Code

1. **Fix Line 151:**
   - Find: `            print(f"✅ Model {model} works correctly")`
   - Replace with: `            print(f"✅ Model {model} works correctly")`
   - (Remove 4 extra spaces at the beginning)

2. **Fix Lines 139-150:**
   - Select lines 139-150
   - Press Tab to indent them

3. **Fix Lines 217-235:**
   - Select lines 217-235  
   - Press Tab to indent them

4. **Fix Lines 243-246:**
   - Select lines 243-246
   - Press Tab to indent them

---

## Quick Test:

After fixing, run:
```powershell
uv run pytest tests/integration/test_document_summarization_integration.py --collect-only
```

Should show: "collected 17 items" with no errors
