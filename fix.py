import os
from pathlib import Path

os.chdir(Path("F:\\Proiecte AI\\santinel"))

# Read requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    lines = f.read().strip().split('\n')

# Add setuptools if missing
if not any('setuptools' in line for line in lines):
    lines.insert(0, "setuptools>=68.0")

# Fix pyjwt version
lines = [line.replace("pyjwt==2.8.1", "pyjwt==2.14.0") for line in lines]

# Write back
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write('\n'.join(lines) + '\n')

print("FIXED: Added setuptools, fixed pyjwt")

# Git
os.system('git add requirements.txt')
os.system('git commit -m "Fix: Add setuptools, update pyjwt to 2.14.0"')
os.system('git push origin main')

print("DONE: Pushed to GitHub")
