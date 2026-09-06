with open("F:\\Proiecte AI\\santinel\\start_api.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Add logging for Deepgram response
old = 'if resp.status_code != 200:'
new = '''print(f"[DEBUG] Deepgram status={resp.status_code}, text={resp.text[:300]}")
    if resp.status_code != 200:'''

content = content.replace(old, new)

with open("F:\\Proiecte AI\\santinel\\start_api.py", 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Deepgram error logging added')