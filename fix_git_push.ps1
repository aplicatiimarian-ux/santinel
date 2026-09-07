cd "F:\Proiecte AI\santinel"
$log = @()
$log += "=== Git Fix Started ==="
$log += (Get-Date).ToString()
$log += ""

# Remove .cache from git
$log += "Removing .cache from git..."
$output = & git rm --cached -r .cache 2>&1
$log += $output
$log += "git rm exit code: $LASTEXITCODE"
$log += ""

# Update .gitignore
$log += "Updating .gitignore..."
$gitignore = @(
    "Claude outputs/",
    "*.env",
    ".env",
    ".env.local",
    ".cache/",
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    ".coverage",
    "venv/"
)
$gitignore | Out-File -FilePath ".gitignore" -Encoding UTF8
$log += ".gitignore updated"
$log += ""

# Stage .gitignore
$log += "Staging .gitignore..."
$output = & git add .gitignore 2>&1
$log += $output
$log += ""

# Commit
$log += "Creating commit..."
$output = & git commit -m "Remove large cache files from git, add .cache to .gitignore" 2>&1
$log += $output
$log += "git commit exit code: $LASTEXITCODE"
$log += ""

# Push
$log += "Pushing to GitHub..."
$output = & git push origin main 2>&1
$log += $output
$log += "git push exit code: $LASTEXITCODE"
$log += ""

$log += "=== Git Fix Completed ==="
$log += (Get-Date).ToString()

# Write log to file
$log | Out-File -FilePath "git_fix_log.txt" -Encoding UTF8 -Force
Write-Host "Log written to git_fix_log.txt"
