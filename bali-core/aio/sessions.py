"""
Extend async session
"""
from contextvars import ContextVar

from sqlalchemy.ext.asyncio.session import (
    AsyncSession as AsyncioSession,
)

session_is_async: ContextVar[bool] = ContextVar(
    'session_is_async', default=False
)


class AsyncSession(AsyncioSession):
    async def __aenter__(self):
        session_is_async.set(True)
        return await super().__aenter__()

    async def __aexit__(self, type_, value, traceback):
        result = await super().__aexit__(type_, value, traceback)
        session_is_async.set(False)
        return result
