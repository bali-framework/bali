from datetime import datetime
from bali.utils import dateparser


def test_parse_dmy_date():
    s = '04/03/2014 22:07:40'
    expect = datetime(2014, 3, 4, 22, 7, 40)
    assert dateparser.parse(s, settings={'DATE_ORDER': 'DMY'}) == expect
