"""
pytest conftest — ensures the backend/ directory is on sys.path
and .env is loaded before any test module imports app code.
"""
import os
import sys
from pathlib import Path

# Make sure 'app' is importable from tests/
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
_env = Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text("utf-8").splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
