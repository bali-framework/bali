import logging
from functools import wraps

from sqla_wrapper import SQLAlchemy
from sqlalchemy.exc import OperationalError
from .models import get_base_model, AwareDateTime

# from core.config import settings

error_logger = logging.getLogger('error')


# noinspection PyPep8Naming
class DB:
    def __init__(self):
        self._session = None

    def connect(self, database_uri, **kwargs):
        kwargs.setdefault("pool_size", 5)
        kwargs.setdefault("pool_recycle", 2 * 60 * 60)

        # developers need to know when the ORM object needs to reload from the db
        kwargs.setdefault("expire_on_commit", False)
        self._session = SQLAlchemy(database_uri, **kwargs)

    def __getattribute__(self, attr, *args, **kwargs):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if not self._session:
                raise Exception('Database session not initialized')

            # BaseModel
            if attr == 'BaseModel':
                return get_base_model(self)

            return getattr(self._session, attr)


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
                        'Deadlock detected. Trying sql transaction once more. Attempts count: %s' %
                        (attempt_count + 1)
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
