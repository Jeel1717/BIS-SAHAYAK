import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://www.bis.gov.in/consumer-overview/grievance-and-complaint/?lang=en'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, context=ctx, timeout=15).read()

from bs4 import BeautifulSoup
soup = BeautifulSoup(raw, 'lxml')

articles = soup.find_all('article')
print('Number of articles:', len(articles))
for i, a in enumerate(articles):
    print(f"Article {i}: class={a.get('class')} text_len={len(a.get_text())}")

# Check where the largest text blocks are
candidates = []
for tag in soup.find_all(['div', 'main', 'section', 'article']):
    cls = ' '.join(tag.get('class') or [])
    tid = tag.get('id') or ''
    tlen = len(tag.get_text(strip=True))
    if tlen > 500:
        candidates.append((tlen, tag.name, cls, tid))

candidates.sort(key=lambda x: x[0], reverse=True)
print('Top 8 candidates by text length:')
for c in candidates[:8]:
    print(c)
