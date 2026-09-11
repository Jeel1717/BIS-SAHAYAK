import urllib.request, ssl
import sys
import io
sys.path.insert(0, '.')

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://www.bis.gov.in/consumer-overview/grievance-and-complaint/?lang=en',
    'https://www.bis.gov.in/consumer-overview/compulsory-registration-scheme/?lang=en',
    'https://www.bis.gov.in/hallmarking-overview/assaying-and-hallmarking-centres/?lang=en',
    'https://www.bis.gov.in/laboratory-overview/?lang=en',
    'https://www.bis.gov.in/consumer-overview/isi-mark/?lang=en',
]

from app.ingestion.extractor import extract_html

# Let's inspect what happens with refined _find_content_root
from bs4 import BeautifulSoup
import re

def refined_extract(raw_bytes, url):
    soup = BeautifulSoup(raw_bytes, "lxml")
    # remove video cards
    for vc in soup.find_all("article", class_=lambda c: c and "video-card" in c):
        vc.decompose()
    for noise in soup.find_all(["script", "style", "nav", "footer", "header", "form"]):
        noise.decompose()
    for noise_el in soup.find_all(class_=re.compile(r"breadcrumb|sidebar|widget|cssmenu|fixheader|top_header|region-main-menu", re.I)):
        noise_el.decompose()

    # Get body or main
    body = soup.body or soup
    lines = []
    seen = set()
    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "dt", "dd"]):
        txt = el.get_text(separator=" ", strip=True)
        if len(txt) < 15:
            continue
        if txt in seen:
            continue
        seen.add(txt)
        lines.append(txt)
    cleaned = "\n\n".join(lines)
    return len(cleaned), cleaned[:200]

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        raw = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        length, sample = refined_extract(raw, url)
        print(f"URL: {url} -> {length} clean chars")
        print(f"Sample: {sample.replace(chr(10), ' ')}")
    except Exception as e:
        print(f"Error {url}: {e}")
