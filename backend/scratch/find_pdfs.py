import urllib.request, re, ssl, sys, io
sys.path.insert(0, '.')

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://www.bis.gov.in/hallmarking-overview/hallmarking-scheme/?lang=en',
    'https://www.bis.gov.in/hallmarking-overview/silver-hallmarking/?lang=en',
    'https://www.bis.gov.in/product-certification-overview/compulsory-certification/?lang=en',
    'https://www.bis.gov.in/consumer-overview/isi-mark/?lang=en',
    'https://www.bis.gov.in/industry-overview/apply-for-isi-mark/?lang=en',
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, context=ctx, timeout=12).read().decode('utf-8', errors='ignore')
        pdfs = set(re.findall(r'https?://[^\s"\'<>]+\.pdf', raw, re.I))
        print(f"\nPage: {url}")
        for p in pdfs:
            if 'bis.gov.in' in p:
                print(f"  - {p}")
    except Exception as e:
        print(f"Error {url}: {e}")
