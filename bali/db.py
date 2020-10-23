import logging
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqla_wrapper import SQLAlchemy

from core.config import settings

error_logger = logging.getLogger('error')

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

db = SQLAlchemy(settings.SQLALCHEMY_DATABASE_URI)


def retry_on_deadlock_decorator(func):
    lock_messages_error = ['Deadlock found', 'Lock wait timeout exceeded']

    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt_count = 0
        while attempt_count < settings.MAXIMUM_RETRY_ON_DEADLOCK:
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                # noinspection PyUnresolvedReferences
                if any(msg in e.message for msg in lock_messages_error) \
                        and attempt_count <= settings.MAXIMUM_RETRY_ON_DEADLOCK:
                    error_logger.error(
                        'Deadlock detected. Trying sql transaction once more. Attempts count: %s'
                        % (attempt_count + 1))
                else:
                    raise
            attempt_count += 1

    return wrapper


def close_connection(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        db.remove()
        return result
    return wrapper
