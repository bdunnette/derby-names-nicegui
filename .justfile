# Justfile for Derby Name Generator

# Set default shell to powershell on Windows
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
# Otherwise use bash
set shell := ["bash", "-c"]

# Run development server by default
server :
    uv run python main.py
