import urllib.request

url = 'http://127.0.0.1:5000/menu'
with urllib.request.urlopen(url) as resp:
    body = resp.read()
    with open('menu_page.html', 'wb') as f:
        f.write(body)
    print('Wrote menu_page.html, length:', len(body))
