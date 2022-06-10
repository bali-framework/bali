"""
Extend async session
"""
from contextvars import ContextVar

from sqlalchemy.ext.asyncio.session import (
    AsyncSession as AsyncioSession,
    _AsyncSessionContextManager as _AsyncioSessionContextManager,
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

    def _maker_context_manager(self):
        """Rewrite AsyncSession Context"""
        return _AsyncSessionContextManager(self)


class _AsyncSessionContextManager(_AsyncioSessionContextManager):
    def __init__(self, async_session):
        self._token = None
        super().__init__(async_session)

    async def __aenter__(self):
        global session_is_async
        self.token = session_is_async.set(True)
        return await super().__aenter__()

    async def __aexit__(self, type_, value, traceback):
        await self.trans.__aexit__(type_, value, traceback)
        await self.async_session.__aexit__(type_, value, traceback)
        session_is_async.reset(self.token)
