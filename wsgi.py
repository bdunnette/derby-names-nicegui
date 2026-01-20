"""WSGI entry point for the FastAPI application.

This file is used for deploying the FastAPI backend with WSGI servers like Gunicorn.
Note: NiceGUI requires its own server and cannot be served via WSGI.

For production deployment:
1. Use this file for the API backend
2. Run NiceGUI separately or use a process manager like supervisord

Example usage with Gunicorn:
    gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker
"""

from api import app
from database import init_db

# Initialize database on startup
init_db()

# Export the FastAPI app for WSGI servers
# This is the application object that WSGI servers will use
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
