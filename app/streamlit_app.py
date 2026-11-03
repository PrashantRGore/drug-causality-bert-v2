"""
Streamlit App Entrypoint Wrapper (Codespaces & Container compatibility)
Delegates directly to the unified root streamlit_app.py.
"""

import sys
from pathlib import Path

# Add root directory to python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute unified main app
main_app_path = root_dir / "streamlit_app.py"
with open(main_app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(main_app_path), "exec")
    exec(code)
