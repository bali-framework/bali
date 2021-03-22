from datetime import datetime

from bali.utils import timezone, dateparser, get_beginning_datetime


def test_parse_dmy_date():
    s = '04/03/2014 22:07:40'
    expect = datetime(2014, 3, 4, 22, 7, 40)
    assert dateparser.parse(s, settings={'DATE_ORDER': 'DMY'}) == expect


def test_get_year_beginning_datetime():
    d = get_beginning_datetime(year=2000)
    assert timezone.make_naive(d) == datetime(2000, 1, 1)


def test_get_month_beginning_datetime():
    d = get_beginning_datetime(year=2000, month=2)
    assert timezone.make_naive(d) == datetime(2000, 2, 1)


def test_get_day_beginning_datetime():
    d = get_beginning_datetime(year=2000, month=2, day=3)
    assert timezone.make_naive(d) == datetime(2000, 2, 3)
