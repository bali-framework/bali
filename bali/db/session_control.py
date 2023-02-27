import functools
from typing import Tuple, TypeVar

from bali.db import db
from sqlalchemy import inspect
from sqlalchemy.exc import InvalidRequestError

__all__ = ["merge_session", "remove_session", "automatic_session_property"]

T = TypeVar("T")


def merge_session(obj: T) -> Tuple[T, bool]:
    if inspect(obj).transient:
        return obj, False

    if inspect(obj).session is not None:
        return obj, False

    try:
        return db.session.merge(obj, load=False), True
    except InvalidRequestError:
        return db.session.merge(obj), True


def remove_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            db.session.remove()

    return wrapper


class automatic_session_property:  # noqa
    def __init__(self, func):
        self._func = func
        self._copy_func_info()

    def _copy_func_info(self):
        if self._func is None:
            return

        for member_name in [
            "__doc__",
            "__name__",
            "__module__",
        ]:
            value = getattr(self._func, member_name)
            setattr(self, member_name, value)

    def __get__(self, instance, _):
        if instance is None:
            return self

        this, is_merged = merge_session(instance)
        try:
            return self._func(this)
        finally:
            is_merged and db.session.remove()

    def __call__(self, func):
        return self.__get__(func, None)
