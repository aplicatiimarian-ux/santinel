import re

with open("F:\\Proiecte AI\\santinel\\start_api.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Find the transcribe function and add logging
old_line = 'if not DEEPGRAM_API_KEY:'
new_line = '''print(f"[DEBUG] /api/transcribe called")
    print(f"[DEBUG] file={file}")
    print(f"[DEBUG] lang={lang}")
    if not DEEPGRAM_API_KEY:'''

content = content.replace(old_line, new_line)

with open("F:\\Proiecte AI\\santinel\\start_api.py", 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Debug logging added')