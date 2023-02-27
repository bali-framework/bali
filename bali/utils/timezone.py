import calendar
import os
from datetime import datetime, date, timedelta, time
from typing import Union
from typing_extensions import Literal

import pytz
from dateutil.relativedelta import relativedelta

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


GRANULARITY = Literal["year", "month", "week", "day"]


def start_of(
    granularity: GRANULARITY,
    value: datetime = None,
    *,
    timezone: StrTzInfoType = None,
) -> datetime:
    value = localtime(value, timezone=timezone)
    if granularity == "year":
        result = value.replace(month=1, day=1)
    elif granularity == "month":
        result = value.replace(day=1)
    elif granularity == "week":
        result = value - timedelta(
            days=calendar.weekday(value.year, value.month, value.day)
        )
    elif granularity == "day":
        result = value
    else:
        raise ValueError("Granularity must be year, month, week or day")

    return make_aware(datetime.combine(result, time.min))


def end_of(
    granularity: GRANULARITY,
    value: datetime = None,
    *,
    timezone: StrTzInfoType = None,
) -> datetime:
    value = localtime(value, timezone=timezone)
    if granularity == "year":
        result = value.replace(month=12, day=31)
    elif granularity == "month":
        result = value + relativedelta(day=1, months=1, days=-1)
    elif granularity == "week":
        result = value + timedelta(
            days=6 - calendar.weekday(value.year, value.month, value.day)
        )
    elif granularity == "day":
        result = value
    else:
        raise ValueError("Granularity must be year, month, week or day")

    return make_aware(datetime.combine(result, time.max))
