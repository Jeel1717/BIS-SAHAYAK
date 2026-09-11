"""
BIS Sahayak — PostgreSQL Connection Test
Phase 5: Database connectivity check

Rules:
- Reads DATABASE_URL from .env only
- NEVER prints, logs, or exposes the password or full URL
- Reports only: success / failure + safe error type
"""

import os
import sys
from pathlib import Path

# ── 1. Load .env without printing it ─────────────────────────────────────────
env_file = Path(__file__).parent / ".env"
if not env_file.exists():
    print("[ERROR] backend/.env not found. Create it from .env.example first.")
    sys.exit(1)

# Manually parse .env (avoids needing python-dotenv for this script)
for line in env_file.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())

# ── 2. Read DATABASE_URL ──────────────────────────────────────────────────────
database_url = os.environ.get("DATABASE_URL", "")

if not database_url:
    print("[ERROR] DATABASE_URL is not set in backend/.env")
    sys.exit(1)

if "[YOUR-PASSWORD]" in database_url:
    print("[ERROR] DATABASE_URL still contains '[YOUR-PASSWORD]'. "
          "Please replace it with your real Supabase password in backend/.env")
    sys.exit(1)

# ── 3. Connect and run SELECT 1 ───────────────────────────────────────────────
print("[INFO]  Attempting PostgreSQL connection...")
print("[INFO]  Host: aws-0-ap-south-1.pooler.supabase.com")
print("[INFO]  Database: postgres (Supabase)")
print()

try:
    import psycopg2

    conn = psycopg2.connect(database_url, connect_timeout=10)
    cursor = conn.cursor()

    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result and result[0] == 1:
        print("=" * 50)
        print("  CONNECTION SUCCESSFUL")
        print("  PostgreSQL responded to SELECT 1 correctly.")
        print("=" * 50)
    else:
        print("[WARN] Connected but SELECT 1 returned unexpected result.")

except psycopg2.OperationalError as e:
    # Strip the URL from the error message before printing
    safe_msg = str(e).replace(database_url, "[DATABASE_URL_REDACTED]")
    print("=" * 50)
    print("  CONNECTION FAILED")
    print(f"  Error type : OperationalError")
    print(f"  Safe detail: {safe_msg.strip()}")
    print("=" * 50)
    print()
    print("Common causes:")
    print("  - Wrong password in DATABASE_URL")
    print("  - Network / firewall blocking port 5432")
    print("  - Supabase project is paused")
    sys.exit(1)

except psycopg2.Error as e:
    safe_msg = str(e).replace(database_url, "[DATABASE_URL_REDACTED]")
    print("=" * 50)
    print("  CONNECTION FAILED")
    print(f"  Error type : {type(e).__name__}")
    print(f"  Safe detail: {safe_msg.strip()}")
    print("=" * 50)
    sys.exit(1)

except Exception as e:
    print("=" * 50)
    print("  CONNECTION FAILED")
    print(f"  Unexpected error type: {type(e).__name__}")
    print("=" * 50)
    sys.exit(1)
