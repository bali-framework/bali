import logging
from functools import wraps

from contextlib import asynccontextmanager
from sqla_wrapper import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import get_base_model

# from core.config import settings

error_logger = logging.getLogger('error')

database_schema_async_maps = [
    ('sqlite://', 'sqlite+aiosqlite://'),
    ('mysql+pymysql://', 'mysql+aiomysql://'),
    ('postgres://', 'postgresql+asyncpg://'),
]


# noinspection PyPep8Naming
class DB:
    def __init__(self):
        self._db = None  # sync engine
        self._async_engine = None  # async engine
        self.async_session = None  # async session maker

    def connect(
        self,
        database_uri,
        engine_options=None,
        session_options=None,
        **kwargs
    ):
        engine_options = engine_options or {}
        engine_options.setdefault("pool_size", 5)
        engine_options.setdefault("pool_recycle", 2 * 60 * 60)

        session_options = session_options or {}
        # developers need to know when the ORM object needs to reload
        # from the db
        session_options.setdefault("expire_on_commit", False)

        # Sync mode db instance
        self._db = SQLAlchemy(
            database_uri,
            engine_options=engine_options,
            session_options=session_options,
        )
        async_database_uri = database_uri
        for sync_schema, async_schema in database_schema_async_maps:
            async_database_uri = async_database_uri.replace(
                sync_schema, async_schema
            )
        self._async_engine = create_async_engine(async_database_uri)

        self.async_session = sessionmaker(
            self._async_engine, class_=AsyncSession, expire_on_commit=False
        )

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if not self._db:
                raise Exception('Database session not initialized')

            # BaseModel
            if attr == 'BaseModel':
                return get_base_model(self)

            return getattr(self._db, attr)


db = DB()

MAXIMUM_RETRY_ON_DEADLOCK: int = 3


def retry_on_deadlock_decorator(func):
    lock_messages_error = ['Deadlock found', 'Lock wait timeout exceeded']

    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt_count = 0
        while attempt_count < MAXIMUM_RETRY_ON_DEADLOCK:
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                # noinspection PyUnresolvedReferences
                if any(msg in e.message for msg in lock_messages_error) \
                        and attempt_count <= MAXIMUM_RETRY_ON_DEADLOCK:
                    error_logger.error(
                        'Deadlock detected. Trying sql transaction once more. Attempts count: %s'
                        % (attempt_count + 1)
                    )
                else:
                    raise
            attempt_count += 1

    return wrapper


def close_connection(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        finally:
            db.remove()

        return result

    return wrapper
