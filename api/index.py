"""
Vercel Serverless Function entry point.
Adds the project root to sys.path so that the backend package is importable.
"""
import sys
import os

# Ensure project root is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.main import app

# Vercel picks up `app` as the ASGI handler for FastAPI
