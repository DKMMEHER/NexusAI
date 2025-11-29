Write-Host "Starting NexusAI Services..." -ForegroundColor Cyan

$PythonPath = ".\.venv\Scripts\python.exe"

# 1. Image Generation Backend (Port 8000)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $PythonPath -m uvicorn ImageGeneration.backend:app --reload --port 8000"
Write-Host "Started Image Generation Backend (Port 8000)" -ForegroundColor Green

# 2. Video Generation Backend (Port 8002)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $PythonPath -m uvicorn VideoGeneration.backend:app --reload --port 8002"
Write-Host "Started Video Generation Backend (Port 8002)" -ForegroundColor Green

# 3. Documents Summarization Backend (Port 8003)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $PythonPath -m uvicorn DocumentsSummarization.backend:app --reload --port 8003"
Write-Host "Started Documents Summarization Backend (Port 8003)" -ForegroundColor Green

# 4. YouTube Transcript Backend (Port 8004)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $PythonPath -m uvicorn YoutubeTranscript.backend:app --reload --port 8004"
Write-Host "Started YouTube Transcript Backend (Port 8004)" -ForegroundColor Green

# 5. Chat Backend (Port 8005)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& $PythonPath -m uvicorn Chat.backend:app --reload --port 8005"
Write-Host "Started Chat Backend (Port 8005)" -ForegroundColor Green

# 6. Frontend
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
Write-Host "Started Frontend" -ForegroundColor Green

Write-Host "All services started!" -ForegroundColor Cyan
