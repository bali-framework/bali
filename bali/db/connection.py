"""
DB Connection

Expose `db` instance, bind managers to model.
"""

from sqla_wrapper import SQLAlchemy, BaseModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from .models import included_models
from ..aio.sessions import AsyncSession
from ..exceptions import DBSetupException

# SQLA-Wrapper 4.x supported session proxy methods
# https://github.com/jpsca/sqla-wrapper/blob/v4.200628/sqla_wrapper/session_proxy.py
SQLA_WRAPPER_SESSION_PROXIES = (
    'query',
    'add',
    'add_all',
    'begin',
    'begin_nested',
    'commit',
    'delete',
    'execute',
    'expire',
    'expire_all',
    'expunge',
    'expunge_all',
    'flush',
    'invalidate',
    'is_modified',
    'merge',
    'prepare',
    'prune',
    'refresh',
    'remove',
    'rollback',
    'scalar',
)


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

        type_checker = TypeChecker(database_uri)

        engine_options = engine_options or {}
        if not type_checker.is_sqlite:
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

        self._async_engine = create_async_engine(type_checker.async_uri)

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
                try:
                    from config import settings
                    self.connect(settings.SQLALCHEMY_DATABASE_URI)
                    if self._db:
                        return self.__getattribute__(attr)
                except ModuleNotFoundError:
                    pass

                raise DBSetupException()

            # BaseModels
            if attr in included_models:
                return included_models[attr](self)

            # Compatible legacy SQLA-Wrapper SessionProxy
            if attr in SQLA_WRAPPER_SESSION_PROXIES:
                return getattr(self._db.s, attr)

            return getattr(self._db, attr)


db = DB()


class TypeChecker:
    """Database URI checker

    check database type and ensure async schema
    """
    def __init__(self, database_uri):
        self.database_uri = database_uri

    @property
    def is_sqlite(self):
        return self.database_uri.startswith('sqlite')

    @property
    def is_mysql(self):
        raise NotImplementedError

    @property
    def is_postgres(self):
        raise NotImplementedError

    @property
    def async_uri(self):
        """
        Transform populate database schema to async format,
        which is used by SQLA-Wrapper
        """
        uri = self.database_uri
        database_schema_async_maps = [
            ('sqlite://', 'sqlite+aiosqlite://'),
            ('mysql+pymysql://', 'mysql+aiomysql://'),
            ('postgres://', 'postgresql+asyncpg://'),
        ]
        for sync_schema, async_schema in database_schema_async_maps:
            uri = uri.replace(sync_schema, async_schema)
        return uri


class AsyncModelDeclarativeMeta(DeclarativeMeta):
    """Make model support async using this metaclass"""
    def __getattribute__(self, attr):
        if attr in ('io', 'aio'):
            manager = super().__getattribute__(attr)
            return setup_manager(manager, self, prefix=attr)

        return super().__getattribute__(attr)

    # noinspection PyMethodParameters
    def __call__(self, *args, **kwargs):
        """
        Given model async supported

            ```python
            # async instance
            async_instance = Model(async=True)
            ```

        model method starts with prefix `async_`
        will transform to replace a copy replace the prefix

        for example, if you define a model with `async_foo`

            ```python
            class User(db.Base):
                async def foo(self):
                    return 'sync result'

                async def async_foo(self):
                    return 'async result'

            # call the method of async instance
            # it will return the "async result"
            user = User(async=True):
            assert user.foo() == 'async result'
            ```
        """

        instance = super().__call__(*args, **kwargs)
        # instance.aio is deprecated, will be removed in 3.5
        instance.aio = self.aio(instance)
        aio = kwargs.pop('aio', False)
        return instance._as_async() if aio else instance


def setup_manager(manager, model, prefix=''):
    if any([manager.db is None, manager.model is None]):
        manager = type(
            f'{prefix.upper()}{manager.__qualname__}',
            manager.__bases__,
            dict(manager.__dict__),
        )
        setattr(manager, 'db', model._db)
        setattr(manager, 'model', model)
    return manager
