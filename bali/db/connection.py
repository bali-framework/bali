import logging
import warnings
from functools import wraps

from sqla_wrapper import SQLAlchemy, BaseModel
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .models import included_models

# TODO: Removed logging according 12factor
error_logger = logging.getLogger('error')


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
        self._db.Model = self._db.registry.generate_base(
            cls=BaseModel,
            name="Model",
            metaclass=AsyncModelDeclarativeMeta,
        )

        async_database_uri = get_async_database_uri(database_uri)
        self._async_engine = create_async_engine(async_database_uri)

        self.async_session = sessionmaker(
            self._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if not self._db:
                raise Exception('Database session not initialized')

            # BaseModels
            if attr in included_models:
                return included_models[attr](self)

            return getattr(self._db, attr)


db = DB()


def get_async_database_uri(database_uri):
    """
    Transform populate database schema to async format,
    which is used by SQLA-Wrapper
    """
    uri = database_uri
    database_schema_async_maps = [
        ('sqlite://', 'sqlite+aiosqlite://'),
        ('mysql+pymysql://', 'mysql+aiomysql://'),
        ('postgres://', 'postgresql+asyncpg://'),
    ]
    for sync_schema, async_schema in database_schema_async_maps:
        uri = uri.replace(sync_schema, async_schema)
    return uri


MAXIMUM_RETRY_ON_DEADLOCK: int = 3


def retry_on_deadlock_decorator(func):
    warnings.warn(
        'retry_on_deadlock_decorator will remove in 3.2',
        DeprecationWarning,
    )

    lock_messages_error = [
        'Deadlock found',
        'Lock wait timeout exceeded',
    ]

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
                        'Deadlock detected. Trying sql transaction once more. '
                        'Attempts count: %s' % (attempt_count + 1)
                    )
                else:
                    raise
            attempt_count += 1

    return wrapper


def close_connection(func):
    warnings.warn(
        'retry_on_deadlock_decorator will remove in 3.2',
        DeprecationWarning,
    )

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        finally:
            db.remove()

        return result

    return wrapper


class AsyncModelDeclarativeMeta(DeclarativeMeta):
    """Make db.BaseModel support async using this metaclass"""
    def __getattribute__(self, attr):
        if attr == 'aio':
            aio = super().__getattribute__(attr)
            if any([aio.db is None, aio.model is None]):
                aio = type(
                    f'Aio{aio.__qualname__}',
                    aio.__bases__,
                    dict(aio.__dict__),
                )
                setattr(aio, 'db', self._db)
                setattr(aio, 'model', self)
            return aio

        return super().__getattribute__(attr)

    # noinspection PyMethodParameters
    def __call__(self, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.aio = self.aio(instance)
        return instance
