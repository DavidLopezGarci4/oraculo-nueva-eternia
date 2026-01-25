import sys
import os
import io
from pathlib import Path

def initialize_runtime():
    """
    Initializes the 3OX runtime environment:
    1. Enforces PYTHONUTF8=1.
    2. Configures stdout/stderr for UTF-8 with surrogateescape.
    3. Adds project root to sys.path.
    """
    # 1. Enforce UTF-8 in environment
    os.environ["PYTHONUTF8"] = "1"

    # 2. Reconfigure standard streams for robust Unicode support
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='surrogateescape')
        sys.stderr.reconfigure(encoding='utf-8', errors='surrogateescape')
    elif not isinstance(sys.stdout, io.TextIOWrapper):
        # Fallback for older environments or specific wrappers
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='surrogateescape', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='surrogateescape', line_buffering=True)

    # 3. Path Resolution
    # We assume this file is in vec3/dev/adapters/
    root_path = Path(__file__).resolve().parent.parent.parent.parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    
    return root_path
