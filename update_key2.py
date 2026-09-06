with open("F:\\Proiecte AI\\santinel\\.env", 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('DEEPGRAM_API_KEY=3299ff932499fe63f9441013e7c918fb0e6073f7', 'DEEPGRAM_API_KEY=a9331c99ae19aad7a78dbcc76e01491530d2f5a4')
with open("F:\\Proiecte AI\\santinel\\.env", 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Updated')