from pydantic import BaseSettings

# noinspection PyUnresolvedReferences
from .application import Bali
from .cache import cache
from .cache_memoize import cache_memoize
from .db import db, transaction
# noinspection PyUnresolvedReferences
from .routing import APIRouter

# Bind transaction to db
setattr(db, 'transaction', transaction)


class Settings(BaseSettings):
    ENABLED_RPC_LOGGING: str = False

_settings = Settings()


def initialize(settings):
    # update basic settings
    if not hasattr(settings, 'ENABLED_RPC_LOGGING'):
        settings.Config.__setattr__(settings, 'ENABLED_RPC_LOGGING', False)

    # load custom settings
    global _settings
    _settings = settings

    # initialize db connections, default enabled db
    # can be disabled by `DISABLE_DB_CONNECTION` settings
    if not getattr(settings, 'DISABLE_DB_CONNECTION', False):
        if not hasattr(settings, 'SQLALCHEMY_DATABASE_URI'):
            raise Exception('Initialized db connection without `SQLALCHEMY_DATABASE_URI` setting')

        db.connect(settings.SQLALCHEMY_DATABASE_URI)

    # initialize cache connections, default enabled db
    # can be disabled by `DISABLED_DB_CONNECTION` settings
    # cache prefix can be custom by `CACHE_PREFIX`
    if not getattr(settings, 'DISABLE_CACHE_CONNECTION', False):
        if not hasattr(settings, 'CACHE_ADDRESS'):
            raise Exception('Initialized cache connection without `CACHE_ADDRESS` setting')

        if not hasattr(settings, 'CACHE_PASSWORD'):
            raise Exception('Initialized cache connection without `CACHE_PASSWORD` setting')

        cache.connect(
            settings.CACHE_ADDRESS,
            password=settings.CACHE_PASSWORD,
            prefix=getattr(settings, 'CACHE_PREFIX', f'{settings.SERVER_NAME}_service')
        )
