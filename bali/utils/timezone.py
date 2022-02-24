import calendar
import os
from datetime import datetime, date, timedelta
from typing import Union

import pytz

TzInfoType = Union[type(pytz.utc), pytz.tzinfo.DstTzInfo]
StrTzInfoType = Union[TzInfoType, str]
DEFAULT_TZ_INFO = "Asia/Jakarta"
NotAwareDescription = "expects an aware datetime"


def get_current_timezone() -> TzInfoType:
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
    assert is_aware(value), NotAwareDescription

    if timezone is None:
        timezone = get_current_timezone()
    elif isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    else:
        pass

    return value.astimezone(timezone).replace(tzinfo=None)


def localtime(value: datetime = None, timezone: StrTzInfoType = None) -> datetime:
    value, timezone = value or now(), timezone or get_current_timezone()
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)

    assert is_aware(value), NotAwareDescription
    return value.astimezone(timezone)


def localdate(value: datetime = None, timezone: StrTzInfoType = None) -> date:
    return localtime(value, timezone).date()


def start_of(
        granularity: str,
        value: datetime = None,
        *,
        timezone: StrTzInfoType = None,
) -> datetime:
    value = localtime(value, timezone)
    if granularity == "year":
        value = value.replace(month=1, day=1)
    elif granularity == "month":
        value = value.replace(day=1)
    elif granularity == "week":
        value = value - timedelta(days=calendar.weekday(value.year, value.month, value.day))
    elif granularity == "day":
        pass
    else:
        raise ValueError("Granularity must be year, month, week or day")

    return value.replace(hour=0, minute=0, second=0, microsecond=0)
