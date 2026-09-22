"""
Graphical User Interface (GUI) / Web Console for JesseCoder.
Provides FastAPI backend with real-time SSE token streaming,
Open-Agent execution console, and TypeScript interactive frontend.
"""

from .server import app

__all__ = ["app"]
