"""Vercel ASGI entrypoint for AutoMind.

This exposes the existing FastAPI application as a Vercel Python Function so
the Vite frontend and API can live on the same Vercel deployment.
"""
from api_server import app
