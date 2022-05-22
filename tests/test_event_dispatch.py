import os

import pytest
from kombu import Connection, Queue, Exchange

from bali.core import _settings
from bali.events import Event, dispatch

amqp_uri = os.getenv('AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672')

exchange_name = 'test_event_dispatch.ms.events'
queue_name = 'test_event_dispatch.events'
_settings.AMQP_CONFIGS = {
    'default': {
        'AMQP_SERVER_ADDRESS': amqp_uri,
        'EXCHANGE_NAME': exchange_name,
        'EXCHANGE_TYPE': 'fanout',
        'QUEUE_NAME': queue_name,
    }
}


class BasicEvent(Event):
    pass


class CustomEvent(Event):
    type: str = 'Customized'
    role: str
    count: int

    def dict(self, *args, **kwargs):
        exclude = kwargs.get('exclude', set({}))
        exclude |= {'payload'}
        kwargs.update(exclude=exclude)
        return super().dict(*args, **kwargs)


class NoConfigEvent(Event):
    __amqp_name__ = 'non-amqp'
    type: str = 'NoConfigEvent'


class TestEvent:
    """Test event define"""
    def test_basic_event(self):
        """
        The basic event json format is

        ```json
        {
            "type": "BasicOccurred",
            "payload": {}
        }
        ```
        """

        event_type = 'BasicOccurred'
        event = BasicEvent(type=event_type)
        assert event.amqp_name == 'default'

        expect_dict = {
            'type': event_type,
            'payload': {},
        }
        assert event.dict() == expect_dict, 'Event export to dict error'

    def test_custom_event(self):
        """
        The custom event json format is

        ```json
        {
            "type": "Customized",
            "role": "designer",
            "count": 5,
        }
        ```
        """
        event_type = 'Customized'
        role = 'designer'
        count = 5
        event = CustomEvent(role=role, count=count)
        assert event.amqp_name == 'default'

        expect_dict = {
            'type': event_type,
            'role': 'designer',
            'count': 5,
        }
        assert event.dict() == expect_dict, 'Event export to dict error'


# Counts event callbacks
basic_counts = 0
basic_multi_counts = 0
custom_counts = 0


class TestEventDispatch:
    """Test event dispatch by AMQP"""
    def test_dispatch_basic_event(self):
        event_type = 'BasicOccurred'
        event = BasicEvent(type=event_type)

        # Bind a queue to receive event message
        conn = Connection(amqp_uri)
        channel = conn.channel()
        exchange = Exchange(exchange_name, type='fanout')
        b = Queue(queue_name, exchange, queue_name, channel=channel)
        b.declare()

        dispatch(event)

        def callback(body, message):
            global basic_counts
            basic_counts += 1
            assert body == event.dict()

        with conn.Consumer(queues=[b], accept=['json'], callbacks=[callback]):
            conn.drain_events(timeout=10)

        global basic_counts
        assert basic_counts == 1

        conn.close()

    def test_dispatch_basic_event_multi_times(self):
        event_type = 'BasicOccurred'
        event = BasicEvent(type=event_type)

        # Bind a queue to receive event message
        conn = Connection(amqp_uri)
        channel = conn.channel()
        exchange = Exchange(exchange_name, type='fanout')
        b = Queue(queue_name, exchange, queue_name, channel=channel)
        b.declare()

        for _ in range(3):
            dispatch(event)

        def callback(body, message):
            global basic_multi_counts
            basic_multi_counts += 1
            assert body == event.dict()

        with conn.Consumer(queues=[b], accept=['json'], callbacks=[callback]):
            conn.drain_events(timeout=20)

        global basic_multi_counts
        assert basic_multi_counts == 3

        conn.close()

    def test_dispatch_custom_event(self):
        event_type = 'Customized'
        role = 'designer'
        count = 5
        event = CustomEvent(role=role, count=count)

        # Bind a queue to receive event message
        conn = Connection(amqp_uri)
        channel = conn.channel()
        exchange = Exchange(exchange_name, type='fanout')
        b = Queue(queue_name, exchange, queue_name, channel=channel)
        b.declare()

        dispatch(event)

        def callback(body, message):
            global custom_counts
            custom_counts += 1
            assert body == event.dict()

        with conn.Consumer(queues=[b], accept=['json'], callbacks=[callback]):
            conn.drain_events(timeout=10)

        global custom_counts
        assert custom_counts == 1

        conn.close()

    def test_dispatch_event_without_amqp_config(self):
        event = NoConfigEvent()
        with pytest.raises(Exception) as ex:
            dispatch(event)
            assert 'AMQP_CONFIGS not set' in ex.__str__()
