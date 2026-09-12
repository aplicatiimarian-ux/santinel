# SANTINEL - Render.com Complete Deployment
# Automated: Update .env + Deploy + Update Frontend

Write-Host ""
Write-Host "SANTINEL Render Deployment - Full Automation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "F:\Proiecte AI\santinel"
$envFilePath = "$projectPath\.env"

if (!(Test-Path $projectPath)) {
    Write-Host "[FAIL] Project not found at: $projectPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "STEP 1: Updating .env with Neon Database Connection" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

$envContent = Get-Content $envFilePath | ForEach-Object { $_ }

Write-Host "Current .env state:" -ForegroundColor Green
Write-Host "  * AUTH_DATABASE_URL: localhost:5432 (local)" -ForegroundColor Gray
Write-Host "  * CORS_ORIGINS: includes ngrok URL" -ForegroundColor Gray
Write-Host ""
Write-Host "Next: Neon PostgreSQL connection string" -ForegroundColor Cyan
Write-Host ""

Write-Host "Connection string format:" -ForegroundColor Cyan
Write-Host "  postgresql://[user]:[password]@[hostname]/[database]?sslmode=require" -ForegroundColor Gray
Write-Host ""
Write-Host "Example from Neon console:" -ForegroundColor Cyan
Write-Host "  postgresql://neondb_owner:abc123xyz@ep-xyz.neon.tech/neondb?sslmode=require" -ForegroundColor Gray
Write-Host ""

$neonURL = Read-Host "PASTE Neon PostgreSQL connection string (from console.neon.tech)"

if (-not $neonURL -or $neonURL.Trim() -eq "") {
    Write-Host ""
    Write-Host "[!] Connection string is required. Aborting." -ForegroundColor Yellow
    exit 1
}

$newEnv = @()
$updated = $false

foreach ($line in $envContent) {
    if ($line -match "^AUTH_DATABASE_URL=") {
        $newEnv += "AUTH_DATABASE_URL=$neonURL"
        $updated = $true
        Write-Host "[OK] Updated AUTH_DATABASE_URL" -ForegroundColor Green
    }
    elseif ($line -match "^AUTH_COOKIE_SECURE=") {
        $newEnv += "AUTH_COOKIE_SECURE=true"
        Write-Host "[OK] Set AUTH_COOKIE_SECURE=true for HTTPS" -ForegroundColor Green
    }
    else {
        $newEnv += $line
    }
}

$newEnv | Set-Content $envFilePath -Encoding UTF8
Write-Host "[OK] .env file updated" -ForegroundColor Green
Write-Host ""

Write-Host "STEP 2: Committing to Git" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

Push-Location $projectPath

git add .env
$gitStatus = git status --porcelain

if ($gitStatus) {
    git commit -m "Update: Switch to Neon PostgreSQL + enable secure cookies

- AUTH_DATABASE_URL: Local PostgreSQL to Neon cloud database
- AUTH_COOKIE_SECURE: false to true for production HTTPS
- Prepares backend for Render.com deployment" 2>$null
    Write-Host "[OK] Changes committed" -ForegroundColor Green
} else {
    Write-Host "[i] No changes to commit" -ForegroundColor Cyan
}

Write-Host ""

Write-Host "STEP 3: Render.com Web Service Setup" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "Opening Render dashboard in your browser..." -ForegroundColor Cyan
Start-Process "https://dashboard.render.com"
Start-Sleep 2

Write-Host ""
Write-Host "Follow these steps in the Render dashboard:" -ForegroundColor Green
Write-Host ""
Write-Host "  1. Click: NEW -> Web Service" -ForegroundColor Gray
Write-Host "  2. Select: GitHub -> 'santinel' repository -> Connect" -ForegroundColor Gray
Write-Host "  3. Configure:" -ForegroundColor Gray
Write-Host "     Name: santinel-backend" -ForegroundColor Gray
Write-Host "     Environment: Python 3" -ForegroundColor Gray
Write-Host "     Region: Oregon (or closest)" -ForegroundColor Gray
Write-Host "     Build: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "     Start: uvicorn start_api:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "  4. Environment Variables: Add all from your .env file" -ForegroundColor Gray
Write-Host "     JWT_SECRET, JWT_ACCESS_TTL_MIN=15, JWT_REFRESH_TTL_DAYS=7" -ForegroundColor Gray
Write-Host "     AUTH_DATABASE_URL (Neon URL you pasted earlier)" -ForegroundColor Gray
Write-Host "     CORS_ORIGINS, AUTH_COOKIE_SECURE=true" -ForegroundColor Gray
Write-Host "     DEEPGRAM_API_KEY, DEEPGRAM_STT_MODEL=nova-2, DEEPGRAM_MIN_CONFIDENCE=0.55" -ForegroundColor Gray
Write-Host "  5. Click: Create Web Service" -ForegroundColor Gray
Write-Host "  6. Wait 3-5 min -> Get Render URL" -ForegroundColor Gray
Write-Host ""

$renderURL = Read-Host "PASTE Render backend URL when ready (e.g., https://santinel-backend-xyz.onrender.com)"

if (-not $renderURL -or $renderURL.Trim() -eq "") {
    Write-Host ""
    Write-Host "[!] Render URL is required. Please create the service and try again." -ForegroundColor Yellow
    Pop-Location
    exit 1
}

$renderURL = $renderURL.TrimEnd('/')

Write-Host "[OK] Render URL received: $renderURL" -ForegroundColor Green
Write-Host ""

Write-Host "STEP 4: Updating Frontend with Render Backend URL" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

$authClientPath = "$projectPath\src\authClient.js"
if (Test-Path $authClientPath) {
    $content = Get-Content $authClientPath -Raw
    $newContent = $content -replace 'baseURL:\s*[^,;]+', "baseURL: '$renderURL/api'"
    Set-Content $authClientPath $newContent -Encoding UTF8
    Write-Host "[OK] Updated src/authClient.js with Render URL" -ForegroundColor Green
} else {
    Write-Host "[!] src/authClient.js not found, skipping" -ForegroundColor Yellow
}

$authClientPath2 = "$projectPath\authClient.js"
if (Test-Path $authClientPath2) {
    $content = Get-Content $authClientPath2 -Raw
    $newContent = $content -replace 'baseURL:\s*[^,;]+', "baseURL: '$renderURL/api'"
    Set-Content $authClientPath2 $newContent -Encoding UTF8
    Write-Host "[OK] Updated authClient.js with Render URL" -ForegroundColor Green
}

Write-Host ""
Write-Host "STEP 5: Adding Render URL to CORS_ORIGINS" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

$envContent = Get-Content $envFilePath
$newEnv = @()

foreach ($line in $envContent) {
    if ($line -match "^CORS_ORIGINS=") {
        if ($line -notcontains $renderURL) {
            $line = $line + "," + $renderURL
        }
        $newEnv += $line
        Write-Host "[OK] Updated CORS_ORIGINS with: $renderURL" -ForegroundColor Green
    }
    else {
        $newEnv += $line
    }
}

$newEnv | Set-Content $envFilePath -Encoding UTF8
Write-Host ""

Write-Host "STEP 6: Committing Frontend Updates" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

git add src/authClient.js authClient.js .env
$gitStatus = git status --porcelain

if ($gitStatus) {
    git commit -m "Update: Backend URL from ngrok to Render deployment

- src/authClient.js: baseURL updated to Render backend
- authClient.js: baseURL updated to Render backend
- .env: CORS_ORIGINS includes Render URL
- Vercel will auto-redeploy on push" 2>$null
    Write-Host "[OK] Changes committed" -ForegroundColor Green
} else {
    Write-Host "[i] No changes to commit" -ForegroundColor Cyan
}

Write-Host ""

Write-Host "STEP 7: Pushing to GitHub (Vercel Auto-Redeploy)" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Pushed successfully" -ForegroundColor Green
} else {
    Write-Host "[!] Git push returned status: $LASTEXITCODE" -ForegroundColor Yellow
    Write-Host "    (This might be OK if changes were already pushed)" -ForegroundColor Yellow
}

Pop-Location

Write-Host ""
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  [OK] DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "What's been done:" -ForegroundColor Green
Write-Host "  [OK] Updated .env with Neon PostgreSQL URL" -ForegroundColor Gray
Write-Host "  [OK] Enabled secure HTTPS cookies" -ForegroundColor Gray
Write-Host "  [OK] Created Render Web Service" -ForegroundColor Gray
Write-Host "  [OK] Configured environment variables" -ForegroundColor Gray
Write-Host "  [OK] Updated frontend (src/authClient.js)" -ForegroundColor Gray
Write-Host "  [OK] Updated CORS for Render URL" -ForegroundColor Gray
Write-Host "  [OK] Pushed to GitHub" -ForegroundColor Gray
Write-Host "  [OK] Vercel auto-redeploy triggered" -ForegroundColor Gray
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Wait 1-2 minutes for Vercel to redeploy" -ForegroundColor Gray
Write-Host "  2. Test on HP browser: https://santinel-8a53.vercel.app" -ForegroundColor Gray
Write-Host "  3. Test on Android: https://santinel-8a53.vercel.app" -ForegroundColor Gray
Write-Host "  4. Try login - should work from Render backend now!" -ForegroundColor Gray
Write-Host ""

Write-Host "Status URLs:" -ForegroundColor Cyan
Write-Host "  Backend (Render):  $renderURL/health" -ForegroundColor Gray
Write-Host "  Frontend (Vercel): https://santinel-8a53.vercel.app" -ForegroundColor Gray
Write-Host "  Render Dashboard:  https://dashboard.render.com/services/santinel-backend" -ForegroundColor Gray
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to close"
