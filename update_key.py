with open("F:\\Proiecte AI\\santinel\\.env", 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('DEEPGRAM_API_KEY=3b43c311cb32c75f819d6907303468bf8f52562e', 'DEEPGRAM_API_KEY=3299ff932499fe63f9441013e7c918fb0e6073f7')
with open("F:\\Proiecte AI\\santinel\\.env", 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ API Key updated')