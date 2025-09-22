import urllib.request

url = 'http://127.0.0.1:5000/menu'
with urllib.request.urlopen(url) as resp:
    body = resp.read()
    print('Status:', resp.status)
    print('Content-Type:', resp.getheader('Content-Type'))
    print('Content-Length header:', resp.getheader('Content-Length'))
    print('Body length:', len(body))
    print('Body repr (first 500 chars):')
    print(repr(body[:500]))
