"""
Vercel Serverless Function entry point.
Vercel's @vercel/python runtime imports this file and looks for an `app` 
or `handler` ASGI/WSGI application object.
"""
from backend.main import app

# Vercel needs `handler` or `app` at the module level
handler = app
