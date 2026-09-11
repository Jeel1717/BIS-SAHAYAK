import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

env_file = Path(".env")
for line in env_file.read_text("utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

url = os.environ.get("DATABASE_URL")
print(f"Creating engine with prepare_threshold=None, NullPool...", flush=True)

engine = create_engine(
    url,
    poolclass=NullPool,
    connect_args={
        "prepare_threshold": None,
        "connect_timeout": 10,
    },
)

print("Attempting connection...", flush=True)
with engine.connect() as conn:
    print("Connected!", flush=True)
    val = conn.execute(text("SELECT 1")).scalar()
    print(f"SELECT 1 result: {val}", flush=True)

print("Success!", flush=True)
