# Deployment Guide

## Production Deployment Options

### Option 1: Separate API and UI (Recommended)

Deploy the FastAPI backend and NiceGUI frontend separately:

#### API Backend (FastAPI)
```bash
# Using Gunicorn with Uvicorn workers
gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Or using Uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8001 --workers 4
```

#### UI Frontend (NiceGUI)
```bash
# Run NiceGUI on a different port
python main.py
```

### Option 2: Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --all-groups

# Expose ports
EXPOSE 8000 8001

# Run both API and UI
CMD ["python", "main.py"]
```

### Option 3: Process Manager (supervisord)

Create `supervisord.conf`:
```ini
[program:derby-api]
command=gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
directory=/path/to/derby-names-nicegui
autostart=true
autorestart=true

[program:derby-ui]
command=python main.py
directory=/path/to/derby-names-nicegui
autostart=true
autorestart=true
```

### Option 4: Systemd Services

Create `/etc/systemd/system/derby-api.service`:
```ini
[Unit]
Description=Derby Names API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/derby-names-nicegui
ExecStart=/path/to/.venv/bin/gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/derby-ui.service`:
```ini
[Unit]
Description=Derby Names UI
After=network.target derby-api.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/derby-names-nicegui
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable derby-api derby-ui
sudo systemctl start derby-api derby-ui
```

### Option 5: PythonAnywhere Deployment

PythonAnywhere is a beginner-friendly hosting platform. **Note**: Only the FastAPI backend can be deployed on the free tier. NiceGUI requires WebSocket support (paid plans only).

#### Setup Steps

1. **Create Account**: Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload Code**:
   ```bash
   # Clone from GitHub in PythonAnywhere Bash console
   git clone https://github.com/yourusername/derby-names-nicegui.git
   cd derby-names-nicegui
   ```

3. **Create Virtual Environment**:
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install uv
   uv sync --group production
   ```

4. **Configure WSGI**: Use the provided `wsgi_pythonanywhere.py` file
   - Go to Web tab → Add new web app → Manual configuration → Python 3.13
   - Copy contents of `wsgi_pythonanywhere.py` to WSGI config file
   - Update `PYTHONANYWHERE_USERNAME` variable

5. **Set Environment Variables** (Web tab):
   ```
   API_PORT=8001
   DATABASE_URL=sqlite:////home/yourusername/derby-names-nicegui/data/derby_names.db
   ```

6. **Reload**: Click green "Reload" button

#### Access Your API
```
https://yourusername.pythonanywhere.com/api/
```

#### Important Limitations
- ⚠️ **NiceGUI not supported on free tier** (WebSockets require paid plan)
- ⚠️ **API only** deployment
- ⚠️ Use absolute paths for SQLite database
- ⚠️ Check error logs in Web tab if issues occur

### Option 6: Heroku Deployment

Heroku provides easy deployment with Git. **Note**: Only the FastAPI backend can be deployed. NiceGUI requires persistent WebSocket connections.

#### Prerequisites
- Heroku account ([signup.heroku.com](https://signup.heroku.com))
- Heroku CLI installed ([devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli))
- Git repository

#### Quick Deploy

1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create Heroku App**:
   ```bash
   heroku create your-derby-names-app
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set API_PORT=8001
   heroku config:set STORAGE_SECRET=$(openssl rand -hex 32)
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Open App**:
   ```bash
   heroku open
   ```

#### Configuration Files

The following files are already configured for Heroku:

- **Procfile**: Defines the web process
  ```
  web: gunicorn wsgi:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
  ```

- **runtime.txt**: Specifies Python version
  ```
  python-3.13.0
  ```

- **app.json**: Heroku app configuration

#### Database Configuration

**SQLite** (default) works for development but has limitations on Heroku:
```bash
# SQLite files are ephemeral on Heroku (lost on dyno restart)
```

**PostgreSQL** (recommended for production):
```bash
# Add Heroku Postgres
heroku addons:create heroku-postgresql:essential-0

# Update your code to use DATABASE_URL
# Heroku automatically sets DATABASE_URL environment variable
```

#### Scaling

```bash
# Scale to multiple dynos
heroku ps:scale web=2

# Check dyno status
heroku ps
```

#### Monitoring

```bash
# View logs
heroku logs --tail

# View app info
heroku info

# Open dashboard
heroku dashboard
```

#### One-Click Deploy

Add this button to your README.md:
```markdown
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
```

#### Important Notes
- ⚠️ **API only**: NiceGUI UI cannot be deployed (WebSocket limitations)
- ⚠️ **Ephemeral filesystem**: Use PostgreSQL instead of SQLite for production
- ⚠️ **Dyno sleep**: Free/Eco dynos sleep after 30 minutes of inactivity
- ⚠️ **Build time**: First deployment may take several minutes
- ✅ **Auto-deploy**: Enable GitHub integration for automatic deployments

## Environment Variables

Create a `.env` file for production:
```env
API_PORT=8001
UI_PORT=8000
DATABASE_URL=sqlite:///data/derby_names.db
STORAGE_SECRET=your-secret-key-here-change-in-production
```

## Nginx Reverse Proxy

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # UI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for NiceGUI
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Required Dependencies for Production

Add to `pyproject.toml`:
```toml
[dependency-groups]
production = [
    "gunicorn>=21.0.0",
]
```

Install:
```bash
uv sync --group production
```
