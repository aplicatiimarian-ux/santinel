#!/usr/bin/env python3
"""
FIX pyjwt version in requirements.txt for Render deploy
pyjwt==2.8.1 doesn't exist → use 2.14.0 (latest available)
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("F:\\Proiecte AI\\santinel")
os.chdir(PROJECT_ROOT)

requirements_path = PROJECT_ROOT / "requirements.txt"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")

def log_error(msg):
    print(f"{RED}[✗]{RESET} {msg}")
    exit(1)

def log_info(msg):
    print(f"{YELLOW}[*]{RESET} {msg}")

print("="*70)
log_info("FIXING requirements.txt — pyjwt version")
print("="*70)

# Read file
log_info(f"Reading: {requirements_path}")
with open(requirements_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix pyjwt version
if "pyjwt==2.8.1" in content:
    log_info("Found: pyjwt==2.8.1 (INVALID VERSION)")
    content = content.replace("pyjwt==2.8.1", "pyjwt==2.14.0")
    log_success("Fixed: pyjwt==2.14.0 (latest available)")
else:
    log_error("pyjwt==2.8.1 not found in requirements.txt")

# Write file
log_info("Writing: requirements.txt")
with open(requirements_path, "w", encoding="utf-8") as f:
    f.write(content)
log_success("File saved")

# Git commit + push
print("\n" + "="*70)
log_info("GIT COMMIT + PUSH")
print("="*70)

os.system('git add requirements.txt')
log_success("git add requirements.txt")

os.system('git commit -m "Fix: Update pyjwt to 2.14.0 (2.8.1 unavailable on PyPI)"')
log_success("git commit created")

os.system('git push origin main')
log_success("git push successful")

print("\n" + "="*70)
log_success("RENDER WILL REDEPLOY AUTOMATICALLY IN 2-3 MINUTES")
print("="*70)
print("""
✓ requirements.txt: pyjwt==2.8.1 → pyjwt==2.14.0
✓ Git commit: Fix: Update pyjwt to 2.14.0
✓ GitHub: Pushed to main (webhook triggers Render)

NEXT: Wait 2-3 minutes, then check Render dashboard
  → https://dashboard.render.com/services/santinel
  → Build should succeed this time
  → Look for [STT], [COACH], [EVAL] in logs
""")
