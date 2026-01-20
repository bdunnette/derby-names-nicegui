"""
PythonAnywhere WSGI Configuration File

This file is specifically for deploying the Derby Names API on PythonAnywhere.
Replace 'yourusername' with your actual PythonAnywhere username.

Instructions:
1. Go to PythonAnywhere Web tab
2. Add new web app → Manual configuration → Python 3.13
3. Edit the WSGI configuration file
4. Copy this content and update the paths
5. Click Reload

Note: NiceGUI UI cannot be deployed on PythonAnywhere free tier due to WebSocket limitations.
Only the FastAPI backend will be available.
"""

import sys
import os

# ============================================================================
# CONFIGURATION - Update these paths with your PythonAnywhere username
# ============================================================================
PYTHONANYWHERE_USERNAME = "yourusername"  # CHANGE THIS!
PROJECT_DIR = f"/home/{PYTHONANYWHERE_USERNAME}/derby-names-nicegui"
VENV_DIR = f"{PROJECT_DIR}/venv"

# ============================================================================
# Add project directory to Python path
# ============================================================================
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ============================================================================
# Activate virtual environment
# ============================================================================
activate_this = os.path.join(VENV_DIR, "bin/activate_this.py")
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {"__file__": activate_this})
else:
    print(
        f"Warning: Virtual environment activation script not found at {activate_this}"
    )

# ============================================================================
# Set environment variables
# ============================================================================
os.environ.setdefault("API_PORT", "8001")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_DIR}/data/derby_names.db")

# ============================================================================
# Import and initialize the FastAPI application
# ============================================================================
try:
    from database import init_db

    # Initialize database on startup
    init_db()
    print("Derby Names API initialized successfully on PythonAnywhere")

except Exception as e:
    print(f"Error initializing application: {e}")
    import traceback

    traceback.print_exc()
    raise

# ============================================================================
# WSGI application is now available as 'application'
# ============================================================================
