"""
FastAPI middleware
"""
from fastapi import Request


async def process_middleware(request: Request, call_next):
    from bali.core import db

    response = await call_next(request)

    try:
        db.remove()
    except Exception:
        pass

    return response
