import urllib.request, ssl, sys, io
sys.path.insert(0, '.')

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.ingestion.sources import BIS_SOURCES
from app.ingestion.fetcher import fetch
from bs4 import BeautifulSoup
import re

# Test the candidate extractor logic
def test_extract(html_bytes, url):
    soup = BeautifulSoup(html_bytes, "lxml")
    
    # Remove video cards and noise tags
    for vc in soup.find_all("article", class_=lambda c: c and "video-card" in c):
        vc.decompose()
    for n in soup.find_all(["script", "style", "nav", "footer", "header", "form", "select", "iframe", "svg"]):
        n.decompose()
    for noise_el in soup.find_all(class_=re.compile(r"breadcrumb|sidebar|widget|cssmenu|fixheader|top_header|region-main-menu|social|cookie", re.I)):
        noise_el.decompose()

    # Find best container
    root = None
    for cls_pattern in ["who_we_area", "entry-content", "page-content", "main-content", "content-area", "post-content"]:
        found = soup.find("div", class_=lambda c: c and cls_pattern in c)
        if found and len(found.get_text(strip=True)) > 200:
            root = found
            break
            
    if not root:
        main_tag = soup.find("main")
        if main_tag and len(main_tag.get_text(strip=True)) > 200:
            root = main_tag
            
    if not root:
        root = soup.body or soup

    lines = []
    seen = set()
    for el in root.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "dt", "dd"]):
        txt = el.get_text(separator=" ", strip=True)
        # Check if meaningful and has English letters
        if len(txt) < 15 or txt in seen:
            continue
        if not re.search(r"[a-zA-Z]{3,}", txt):
            continue
        seen.add(txt)
        lines.append(txt)
        
    cleaned = "\n\n".join(lines)
    return len(cleaned)

# Let's test on 6 of the previously failed URLs
failed_urls = [
    "https://www.bis.gov.in/consumer-overview/grievance-and-complaint/?lang=en",
    "https://www.bis.gov.in/consumer-overview/compulsory-registration-scheme/?lang=en",
    "https://www.bis.gov.in/hallmarking-overview/assaying-and-hallmarking-centres/?lang=en",
    "https://www.bis.gov.in/hallmarking-overview/silver-hallmarking/?lang=en",
    "https://www.bis.gov.in/laboratory-overview/?lang=en",
    "https://www.bis.gov.in/industry-overview/apply-for-isi-mark/?lang=en",
]

for u in failed_urls:
    res = fetch(u)
    if res.ok:
        l = test_extract(res.content, u)
        print(f"URL: {u} -> Extracted {l} clean chars")
    else:
        print(f"Fetch failed for {u}: {res.error}")
