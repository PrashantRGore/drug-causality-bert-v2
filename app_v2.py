"""
Legacy Entrypoint Wrapper: app_v2.py
Delegates to the modern, unified, modular streamlit_app.py.
"""

from pathlib import Path

main_app_path = Path(__file__).resolve().parent / "streamlit_app.py"
with open(main_app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(main_app_path), "exec")
    exec(code)
