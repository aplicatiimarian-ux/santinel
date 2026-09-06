with open('start_api.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('user: dict = Depends(get_current_user),', '# user: dict = Depends(get_current_user),')
with open('start_api.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')