from datetime import datetime

from bali.utils import (
    ParseDict,
    MessageToDict,
    timezone,
    dateparser,
    get_beginning_datetime,
)
from tests.test_services.protos import helloworld_pb2 as pb2


class TestProtobufConverter:
    def test_parse_dict(self):
        d = {'name': 'protobuf'}
        message = ParseDict(d, pb2.HelloRequest())
        assert message

    def test_message_to_dict(self):
        message = pb2.HelloRequest(name='protobuf')
        d = MessageToDict(message)
        assert 'name' in d
        assert d['name'] == 'protobuf'


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
