# SANTINEL DEPLOYMENT SCRIPT - Run this in PowerShell as Administrator
# This script fixes the git blocker and deploys to Vercel

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SANTINEL DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Download BFG if not present
$BFGPath = "F:\Tools\bfg-1.14.0.jar"
$BFGUrl = "https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar"

Write-Host "[1/6] Checking for BFG Repo-Cleaner..." -ForegroundColor Yellow
if (-not (Test-Path $BFGPath)) {
    Write-Host "     Downloading BFG..." -ForegroundColor Yellow
    $ToolsDir = "F:\Tools"
    if (-not (Test-Path $ToolsDir)) {
        New-Item -ItemType Directory -Path $ToolsDir -Force | Out-Null
    }
    Invoke-WebRequest -Uri $BFGUrl -OutFile $BFGPath -ErrorAction Stop
    Write-Host "     ✓ BFG downloaded to $BFGPath" -ForegroundColor Green
} else {
    Write-Host "     ✓ BFG already present at $BFGPath" -ForegroundColor Green
}

# Step 2: Navigate to repo
Write-Host "[2/6] Navigating to santinel repository..." -ForegroundColor Yellow
$RepoPath = "F:\Proiecte AI\santinel"
if (-not (Test-Path $RepoPath)) {
    Write-Host "     ✗ Repository not found at $RepoPath" -ForegroundColor Red
    exit 1
}
Set-Location $RepoPath
Write-Host "     ✓ In repository at $RepoPath" -ForegroundColor Green

# Step 3: Run BFG to delete the large blob
Write-Host "[3/6] Running BFG to remove 138.49 MB blob..." -ForegroundColor Yellow
$BlobId = "d01c3014881c9c6f3133c182f3d2887eb6ca1c789a7538c5c007196857a0a6a9"
java -jar $BFGPath --delete-files $BlobId
if ($LASTEXITCODE -ne 0) {
    Write-Host "     ✗ BFG failed" -ForegroundColor Red
    exit 1
}
Write-Host "     ✓ BFG completed" -ForegroundColor Green

# Step 4: Force cleanup - expire reflog
Write-Host "[4/6] Cleaning git reflog..." -ForegroundColor Yellow
git reflog expire --expire=now --all
Write-Host "     ✓ Reflog expired" -ForegroundColor Green

# Step 5: Aggressive garbage collection
Write-Host "[5/6] Running garbage collection (this may take 1-2 minutes)..." -ForegroundColor Yellow
git gc --prune=now --aggressive
if ($LASTEXITCODE -ne 0) {
    Write-Host "     ✗ Git gc failed" -ForegroundColor Red
    exit 1
}
Write-Host "     ✓ Garbage collection complete" -ForegroundColor Green

# Step 6: Push to GitHub
Write-Host "[6/6] Pushing to GitHub (force push)..." -ForegroundColor Yellow
git push origin main --force
if ($LASTEXITCODE -eq 0) {
    Write-Host "     ✓ Push successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "SUCCESS! Vercel will deploy in 2-3 minutes" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Watch: https://vercel.com/dashboard" -ForegroundColor Cyan
    Write-Host "2. Look for green 'DEPLOYMENT SUCCESSFUL'" -ForegroundColor Cyan
    Write-Host "3. Your live URL: https://santinel-XXXXX.vercel.app" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "     ✗ Push failed" -ForegroundColor Red
    exit 1
}
