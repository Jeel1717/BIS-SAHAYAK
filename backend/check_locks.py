import os
from pathlib import Path
import psycopg

env_file = Path(".env")
for line in env_file.read_text("utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get("DATABASE_URL").replace("+psycopg", "")
conn = psycopg.connect(url, connect_timeout=10)
cur = conn.cursor()

# Check blocking locks
cur.execute("""
    SELECT
        pid,
        usename,
        state,
        query,
        age(clock_timestamp(), query_start) as duration
    FROM pg_stat_activity
    WHERE state != 'idle'
      AND pid != pg_backend_pid();
""")
rows = cur.fetchall()
print(f"Active non-idle processes: {len(rows)}")
for r in rows:
    print(f"PID: {r[0]} | User: {r[1]} | State: {r[2]} | Duration: {r[4]} | Query: {r[3][:100]}")

# Also check pg_locks on chat_sessions
cur.execute("""
    SELECT pid, locktype, mode, granted
    FROM pg_locks
    WHERE relation = 'chat_sessions'::regclass;
""")
locks = cur.fetchall()
print(f"Locks on chat_sessions: {len(locks)}")
for l in locks:
    print(f"Lock: {l}")

conn.close()
