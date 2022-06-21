import json
import os

import amqp
import pytest
from kombu import Connection, Exchange, Queue

from bali.core import _settings
from bali.decorators import event_handler
from bali.events import Event, dispatch, handle

amqp_uri = os.getenv('AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672')

_settings.AMQP_CONFIGS = {
    'default': {
        'AMQP_SERVER_ADDRESS': amqp_uri,
        'EXCHANGE_NAME': 'HELLO_WORLD_TEST',
        'EXCHANGE_TYPE': 'fanout'
    }
}
_settings.EVENT_TYPE_TO_AMQP = {'test0': 'default', 'test1': 'default'}


class MockMessage:
    def ack(self):
        pass


class TestHandle:
    @event_handler(event_type='test0')
    def call_test0(self, event: Event):
        print('test0 received:', event, type(event))
        print(os.path.dirname('bbb.txt'))
        return event

    @event_handler(event_type='test1')
    def call_test1(self, event):
        print('test1 received:', event, type(event))
        print(os.path.basename('aaa.txt'))


def test_when_message_body_is_str():
    body = '{"type":"hello", "payload":""}'
    res = TestHandle().call_test0(body, message=MockMessage())
    assert res is None
    body = '{"type": "test0", "payload": ""}'
    res = TestHandle().call_test0(body, message=MockMessage())
    assert res == Event(**json.loads(body))


def test_when_message_body_is_dict():
    event = {"type": "hello", "payload": ""}
    res = TestHandle().call_test0(event, message=MockMessage())
    assert res is None
    event = {"type": "test0", "payload": ""}
    res = TestHandle().call_test0(event, message=MockMessage())
    assert res == Event(**event)


def teardown_function():

    # Removed test service's queues
    service_abbr = 'product'
    conn = Connection(amqp_uri)
    channel = conn.channel()
    exchange = Exchange('ms.events', type='fanout')
    queue_name = f'{service_abbr}.events'

    b = Queue(queue_name, exchange, queue_name, channel=channel)
    b.delete()
    conn.close()


def test_event_dispatch():
    _settings.AMQP_CONFIGS = {
        'default': {
            'AMQP_SERVER_ADDRESS': amqp_uri,
            'EXCHANGE_NAME': 'HELLO_WORLD_TEST',
            'EXCHANGE_TYPE': 'fanout'
        }
    }
    _settings.EVENT_TYPE_TO_AMQP = {'test0': 'default', 'test1': 'default'}
    for i in range(100):
        event = Event(type='test0', payload={'hello': 'world2222222'})
        assert dispatch(event)
    for i in range(100):
        event = Event(type='test1', payload={'hello': 'world1111111'})
        assert dispatch(event)


handle()


def test_event_handler(mocker):
    mocker.patch('os.path.basename')
    mocker.patch('os.path.dirname')
    handle()
    os.path.basename.assert_called_with('aaa.txt')
    os.path.dirname.assert_called_with('bbb.txt')


def test_queue_declared_in_event_handler(mocker):
    # 1. Define a `Product` service
    service_abbr = 'product'
    _settings.AMQP_CONFIGS = {
        'default': {
            'AMQP_SERVER_ADDRESS': amqp_uri,
            'EXCHANGE_NAME': 'ms.events',
            'EXCHANGE_TYPE': 'fanout',
            'QUEUE_NAME': f'{service_abbr}.events',
        }
    }
    # 2. Ensure RabbitMQ has no queue for `Product` service
    conn = Connection(amqp_uri)
    channel = conn.channel()
    exchange = Exchange('ms.events', type='fanout')
    queue_name = f'{service_abbr}.events'

    b = Queue(queue_name, exchange, queue_name, channel=channel)
    with pytest.raises(amqp.exceptions.NotFound):
        b.queue_declare(passive=True)

    # 3. Launch `Product` service's handle
    from bali.decorators import event_handler

    @event_handler('UserCreated')
    def handle_product_created(event):
        pass

    handle()
    # 4. Assert `product.events` queue exists，and bind to exchange `ms.events`
    b = Queue(queue_name, exchange, queue_name, channel=channel)
    assert b.queue_declare(passive=True)

    # clean
    b.delete()
    conn.close()
