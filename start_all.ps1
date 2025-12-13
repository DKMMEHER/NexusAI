$PythonPath = "c:\Study\GenAI\Project\NexusAI\.venv\Scripts\python.exe"
$EnvPath = "c:\Study\GenAI\Project\NexusAI\.env"
$ParentEnvPath = "c:\Study\GenAI\.env"

Write-Host "Starting NexusAI Backend Services using $PythonPath..." -ForegroundColor Green

# 1. Check for .env file
if (-not (Test-Path $EnvPath)) {
    Write-Host "No .env file found in project root." -ForegroundColor Yellow
    if (Test-Path $ParentEnvPath) {
        Write-Host "Found .env in parent directory. Copying to project root..." -ForegroundColor Cyan
        Copy-Item $ParentEnvPath $EnvPath
        Write-Host "Success: Copied .env file." -ForegroundColor Green
    } else {
        Write-Error "CRITICAL: Could not find .env file in project or parent directory!"
        Write-Error "Please create a .env file with GEMINI_API_KEY."
        exit 1
    }
}

if (-not (Test-Path $PythonPath)) {
    Write-Error "Python executable not found at $PythonPath. Please verify the venv location."
    exit 1
}

# Function to start a process in a new window with correct Working Directory
function Start-Service {
    param (
        [string]$Name,
        [string]$Port,
        [string]$Command
    )
    Write-Host "Starting $Name on port $Port..."
    # Explicitly set WorkingDirectory to current location
    $CurrentDir = Get-Location
    Start-Process powershell -WorkingDirectory "$CurrentDir" -ArgumentList "-NoExit", "-Command", "& { $Command }"
}

# Image Generation
Start-Service -Name "Image Generation" -Port "8000" -Command "& '$PythonPath' -m uvicorn ImageGeneration.backend:app --port 8000 --reload"

# Video Generation
Start-Service -Name "Video Generation" -Port "8002" -Command "& '$PythonPath' -m uvicorn VideoGeneration.backend:app --port 8002 --reload"

# Documents Summarization
Start-Service -Name "Documents Summarization" -Port "8003" -Command "& '$PythonPath' -m uvicorn DocumentsSummarization.backend:app --port 8003 --reload"

# YouTube Transcript
Start-Service -Name "YouTube Transcript" -Port "8004" -Command "& '$PythonPath' -m uvicorn YoutubeTranscript.backend:app --port 8004 --reload"

# Chat
Start-Service -Name "Chat" -Port "8005" -Command "& '$PythonPath' -m uvicorn Chat.backend:app --port 8005 --reload"

# Director
Start-Service -Name "Director" -Port "8006" -Command "& '$PythonPath' -m uvicorn Director.backend:app --port 8006 --reload"

Write-Host "All services launch commands issued." -ForegroundColor Cyan
Write-Host "Please check the opened windows for logs."
