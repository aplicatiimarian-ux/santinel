#!/usr/bin/env python3
"""
SANTINEL AUTO-UPDATE start_api.py - V2
Automatically adds STT/Coach/Eval route imports and creates startup event
"""

import os
import sys
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")

def log_error(msg):
    print(f"{RED}[✗]{RESET} {msg}")
    sys.exit(1)

def log_info(msg):
    print(f"{YELLOW}[*]{RESET} {msg}")

PROJECT_ROOT = Path("F:\\Proiecte AI\\santinel")
os.chdir(PROJECT_ROOT)

start_api_path = PROJECT_ROOT / "backend" / "start_api.py"

if not start_api_path.exists():
    log_error(f"start_api.py not found at {start_api_path}")

log_info(f"Reading: {start_api_path}")
with open(start_api_path, "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================================
# STEP 1: ADD IMPORTS
# ============================================================================
log_info("=== STEP 1: Adding imports ===")

imports_to_add = [
    "from backend.services.stt_cascade_service import setup_stt_routes",
    "from backend.services.coach_output_service import setup_coach_routes",
    "from backend.services.evaluation_service import setup_evaluation_routes"
]

# Check if imports already exist
if "from backend.services.stt_cascade_service import setup_stt_routes" in content:
    log_success("Imports already present")
else:
    # Find last import line (from/import statement)
    lines = content.split("\n")
    last_import_idx = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith("import ") or stripped.startswith("from ")) and not stripped.startswith("import tempfile"):
            last_import_idx = i

    if last_import_idx == -1:
        log_error("No imports found - cannot determine insertion point")

    # Insert new imports after last import
    for new_import in imports_to_add:
        lines.insert(last_import_idx + 1, new_import)
        last_import_idx += 1

    content = "\n".join(lines)
    log_success("Imports added")

# ============================================================================
# STEP 2: CREATE STARTUP EVENT FUNCTION
# ============================================================================
log_info("=== STEP 2: Creating startup event function ===")

startup_code = '''

# ============================================================================
# Startup event: Initialize STT/Coach/Eval routes
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize all service routes on app startup"""
    await setup_stt_routes(app)
    await setup_coach_routes(app, None, None)  # framework_service & tts_service injected from context
    await setup_evaluation_routes(app)
'''

# Check if startup event already exists
if '@app.on_event("startup")' in content:
    log_success("Startup event already present")
else:
    # Find the line with "app = FastAPI"
    lines = content.split("\n")
    app_creation_idx = -1

    for i, line in enumerate(lines):
        if "app = FastAPI" in line:
            app_creation_idx = i
            break

    if app_creation_idx == -1:
        log_error("Could not find app = FastAPI line")

    # Find the end of the middleware/router setup (look for first route definition or auth_router include)
    insert_idx = app_creation_idx + 1
    for i in range(app_creation_idx + 1, len(lines)):
        line = lines[i].strip()
        if "app.include_router" in line or "@app." in line:
            insert_idx = i
            break

    # Insert startup event before first route/router
    lines.insert(insert_idx, startup_code)
    content = "\n".join(lines)
    log_success("Startup event created and inserted")

# ============================================================================
# STEP 3: SAVE FILE
# ============================================================================
log_info("=== STEP 3: Saving updated file ===")

with open(start_api_path, "w", encoding="utf-8") as f:
    f.write(content)

log_success("File saved successfully")

print("\n" + "="*70)
log_success("start_api.py UPDATED SUCCESSFULLY")
print("="*70)
print("""
✓ Imports added:
  - from backend.services.stt_cascade_service import setup_stt_routes
  - from backend.services.coach_output_service import setup_coach_routes
  - from backend.services.evaluation_service import setup_evaluation_routes

✓ Startup event created with route initialization:
  - @app.on_event("startup")
  - await setup_stt_routes(app)
  - await setup_coach_routes(app, framework_service, tts_service)
  - await setup_evaluation_routes(app)

NEXT: Git commit and push
  cd F:\\Proiecte AI\\santinel
  git add backend/start_api.py
  git commit -m "Fix: Add STT/Coach/Eval route initialization"
  git push origin main
""")
