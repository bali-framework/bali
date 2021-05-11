import os
from datetime import datetime
from typing import Union

import pytz

TzInfoType = Union[type(pytz.utc), pytz.tzinfo.DstTzInfo]
StrTzInfoType = Union[TzInfoType, str]
DEFAULT_TZ_INFO = "Asia/Jakarta"


def get_current_timezone() -> TzInfoType:
    """set default value *may* change historical code behaviour"""
    tz_info = os.environ.get("TZ", DEFAULT_TZ_INFO)
    return pytz.timezone(tz_info)


def get_current_timezone_name() -> str:
    return get_current_timezone().tzname(None)


def now() -> datetime:
    return datetime.now(pytz.utc)


def is_aware(value: datetime) -> bool:
    return value.utcoffset() is not None


def is_naive(value: datetime) -> bool:
    return value.utcoffset() is None


def make_aware(
        value: datetime,
        *,
        timezone: StrTzInfoType = None,
        is_dst: bool = False,
) -> datetime:
    assert is_naive(value), "expects a naive datetime"

    if timezone is None:
        timezone = get_current_timezone()
    elif isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    else:
        pass

    return timezone.localize(value, is_dst=is_dst)


def make_naive(
        value: datetime,
        *,
        timezone: StrTzInfoType = None,
) -> datetime:
    assert is_aware(value), "expects an aware datetime"

    if timezone is None:
        timezone = get_current_timezone()
    elif isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    else:
        pass

    return value.astimezone(timezone).replace(tzinfo=None)
