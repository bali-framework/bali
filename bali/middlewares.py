"""
FastAPI middleware
"""
from fastapi import Request


async def process_middleware(request: Request, call_next):
    from bali.core import db

    try:
        response = await call_next(request)
    except Exception:
        raise
    else:
        return response
    finally:

        # remove db session when FastAPI request ended
        try:
            db.remove()
        except Exception:
            pass
