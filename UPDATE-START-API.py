#!/usr/bin/env python3
"""
SANTINEL AUTO-UPDATE start_api.py
Automatically adds STT/Coach/Eval route imports and initialization
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
    # Find last import line
    lines = content.split("\n")
    last_import_idx = -1

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    if last_import_idx == -1:
        log_error("No imports found in file - cannot determine insertion point")

    # Insert new imports after last import
    for new_import in imports_to_add:
        lines.insert(last_import_idx + 1, new_import)
        last_import_idx += 1

    content = "\n".join(lines)
    log_success("Imports added")

# ============================================================================
# STEP 2: ADD ROUTE INITIALIZATION IN @app.on_event("startup")
# ============================================================================
log_info("=== STEP 2: Adding route initialization ===")

startup_marker = '@app.on_event("startup")'
if startup_marker not in content:
    log_error(f'Could not find {startup_marker} - manual update needed')

# Check if routes already initialized
if "await setup_stt_routes(app)" in content:
    log_success("Routes already initialized")
else:
    # Find the startup function
    lines = content.split("\n")
    startup_idx = -1

    for i, line in enumerate(lines):
        if '@app.on_event("startup")' in line:
            startup_idx = i
            break

    if startup_idx == -1:
        log_error("Could not find startup function")

    # Find the first line inside the function (async def or def)
    func_start_idx = -1
    for i in range(startup_idx + 1, len(lines)):
        if "async def" in lines[i] or "def " in lines[i]:
            func_start_idx = i
            break

    if func_start_idx == -1:
        log_error("Could not find function definition after @app.on_event")

    # Find indentation of function body
    func_line = lines[func_start_idx]
    base_indent = len(func_line) - len(func_line.lstrip())
    body_indent = base_indent + 4
    indent_str = " " * body_indent

    # Find first statement in function body
    first_stmt_idx = -1
    for i in range(func_start_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#"):
            first_stmt_idx = i
            break

    if first_stmt_idx == -1:
        log_error("Could not find function body")

    # Insert route initialization calls
    route_calls = [
        f"{indent_str}await setup_stt_routes(app)",
        f"{indent_str}await setup_coach_routes(app, framework_service, tts_service)",
        f"{indent_str}await setup_evaluation_routes(app)"
    ]

    for idx, call in enumerate(route_calls):
        lines.insert(first_stmt_idx + idx, call)

    content = "\n".join(lines)
    log_success("Route initialization added")

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

✓ Route initialization added in @app.on_event("startup"):
  - await setup_stt_routes(app)
  - await setup_coach_routes(app, framework_service, tts_service)
  - await setup_evaluation_routes(app)

NEXT: Git commit and push
  cd F:\\Proiecte AI\\santinel
  git add backend/start_api.py
  git commit -m "Fix: Add STT/Coach/Eval route initialization"
  git push origin main
""")
