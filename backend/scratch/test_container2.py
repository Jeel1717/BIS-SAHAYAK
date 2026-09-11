import urllib.request, ssl
from bs4 import BeautifulSoup
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://www.bis.gov.in/consumer-overview/grievance-and-complaint/?lang=en',
    'https://www.bis.gov.in/consumer-overview/compulsory-registration-scheme/?lang=en',
    'https://www.bis.gov.in/hallmarking-overview/assaying-and-hallmarking-centres/?lang=en',
    'https://www.bis.gov.in/laboratory-overview/?lang=en',
]

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        raw = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        soup = BeautifulSoup(raw, 'lxml')
        # Remove header, nav, footer, video-card
        for n in soup.find_all(['header', 'footer', 'nav', 'script', 'style']):
            n.decompose()
        for a in soup.find_all('article', class_=lambda c: c and 'video-card' in c):
            a.decompose()
        for c in soup.find_all(class_=re.compile(r'top_header|fixheader|main-menu|cssmenu|breadcrumb', re.I)):
            c.decompose()
        
        # Check remaining h1, h2, p
        ps = soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])
        text_samples = [p.get_text(strip=True) for p in ps if len(p.get_text(strip=True)) > 20]
        print(f"\n=== URL: {url} ===")
        print(f"Total elements: {len(text_samples)}")
        for s in text_samples[:4]:
            print(f"  - {s[:100]}...")
    except Exception as e:
        print(f"Error {url}: {e}")
