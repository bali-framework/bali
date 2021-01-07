"""
FastAPI middleware
"""
from fastapi import Request


async def process_middleware(request: Request, call_next):
    from bali.core import db

    response = await call_next(request)

    # remove db session when FastAPI request ended
    try:
        db.remove()
    except Exception:
        pass

    return response
