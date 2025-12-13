Write-Host "Stopping all NexusAI services..." -ForegroundColor Yellow

# Kill Python (Backend)
try {
    Write-Host "Killing Python processes..."
    taskkill /F /IM python.exe
} catch {
    Write-Host "No Python processes running or access denied."
}

# Kill Node (Frontend)
try {
    Write-Host "Killing Node processes..."
    taskkill /F /IM node.exe
} catch {
    Write-Host "No Node processes running or access denied."
}

Write-Host "All services stopped." -ForegroundColor Green
