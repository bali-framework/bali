from datetime import datetime

import pytz
import pytest

from bali.utils import timezone


def test_get_current_timezone():
    assert timezone.get_current_timezone() == pytz.timezone(timezone.DEFAULT_TZ_INFO)


def test_get_current_timezone_name():
    assert timezone.get_current_timezone_name() == pytz.timezone(timezone.DEFAULT_TZ_INFO).tzname(None)


def test_now():
    now = timezone.now()
    assert now.utcoffset() is not None


def test_is_aware():
    now = datetime.now()
    assert not timezone.is_aware(now)


def test_is_naive():
    now = datetime.now()
    assert timezone.is_naive(now)


def test_make_aware():
    d = timezone.make_aware(datetime.now())
    assert d.tzinfo.tzname(None) == timezone.get_current_timezone().tzname(None)

    d = timezone.make_aware(datetime.now(), timezone="Asia/Shanghai")
    assert d.tzinfo.tzname(None) != timezone.get_current_timezone().tzname(None)

    d = timezone.now()
    with pytest.raises(AssertionError):
        timezone.make_aware(d)


def test_make_naive():
    d = timezone.make_naive(timezone.now())
    assert d.tzinfo is None

    d = timezone.make_naive(timezone.now(), timezone="Asia/Shanghai")
    assert d.tzinfo is None

    d = datetime.now()
    with pytest.raises(AssertionError):
        timezone.make_naive(d)
