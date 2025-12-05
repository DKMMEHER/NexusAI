Write-Host "Starting NexusAI Services..." -ForegroundColor Cyan

$CurrentDir = Get-Location
$PythonPath = "$CurrentDir\.venv\Scripts\python.exe"

# 1. Image Generation Backend (Port 8000)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn ImageGeneration.backend:app --reload --port 8000" -WorkingDirectory $CurrentDir
Write-Host "Started Image Generation Backend (Port 8000)" -ForegroundColor Green

# 2. Video Generation Backend (Port 8002)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn VideoGeneration.backend:app --reload --port 8002" -WorkingDirectory $CurrentDir
Write-Host "Started Video Generation Backend (Port 8002)" -ForegroundColor Green

# 3. Documents Summarization Backend (Port 8003)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn DocumentsSummarization.backend:app --reload --port 8003" -WorkingDirectory $CurrentDir
Write-Host "Started Documents Summarization Backend (Port 8003)" -ForegroundColor Green

# 4. YouTube Transcript Backend (Port 8004)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn YoutubeTranscript.backend:app --reload --port 8004" -WorkingDirectory $CurrentDir
Write-Host "Started YouTube Transcript Backend (Port 8004)" -ForegroundColor Green

# 5. Chat Backend (Port 8005)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn Chat.backend:app --reload --port 8005" -WorkingDirectory $CurrentDir
Write-Host "Started Chat Backend (Port 8005)" -ForegroundColor Green

# 6. Director Backend (Port 8006)
Start-Process -FilePath $PythonPath -ArgumentList "-m uvicorn Director.backend:app --reload --port 8006" -WorkingDirectory $CurrentDir
Write-Host "Started Director Backend (Port 8006)" -ForegroundColor Green

# 7. Frontend
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WorkingDirectory "$CurrentDir\frontend"
Write-Host "Started Frontend" -ForegroundColor Green

Write-Host "All services started!" -ForegroundColor Cyan
