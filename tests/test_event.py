import os

import amqp
import pytest
from kombu import Connection, Exchange, Queue

from bali.core import _settings
from bali.decorators import event_handler
from bali.events import Event, dispatch, handle

_settings.AMQP_CONFIGS = {
    'default':
        {
            'AMQP_SERVER_ADDRESS':
                os.getenv(
                    'AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672'
                ),
            'EXCHANGE_NAME':
                'HELLO_WORLD_TEST',
            'EXCHANGE_TYPE':
                'fanout',
            'QUEUE_NAME':
                'QUEQUE_C'
        }
}
_settings.EVENT_TYPE_TO_AMQP = {'test0': 'default', 'test1': 'default'}


@event_handler(event_type='test0')
def call_test0(event):
    print('test0 received:', event)
    print(os.path.dirname('bbb.txt'))


@event_handler(event_type='test1')
def call_test1(event):
    print('test1 received:', event)
    print(os.path.basename('aaa.txt'))


def test_event_dispatch():
    _settings.AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS':
                    os.getenv(
                        'AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672'
                    ),
                'EXCHANGE_NAME':
                    'HELLO_WORLD_TEST',
                'EXCHANGE_TYPE':
                    'fanout'
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
    _settings.AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS':
                    os.getenv(
                        'AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672'
                    ),
                'EXCHANGE_NAME':
                    'HELLO_WORLD_A',
                'EXCHANGE_TYPE':
                    'fanout',
                'QUEUE_NAME':
                    'QUEQUE_E'
            }
    }

    # 1. Define a `Product` service
    service_abbr = 'product22'

    @event_handler(event_type=service_abbr)
    def call_back(event):
        print('test_a received:', event)

    # 2. Ensure RabbitMQ has no queue for `Product` service
    amqp_config = _settings.AMQP_CONFIGS.get('default')
    amqp_server_address = amqp_config.get('AMQP_SERVER_ADDRESS')
    conn = Connection(amqp_server_address)
    channel = conn.channel()
    exchange = Exchange(
        amqp_config.get('EXCHANGE_NAME'),
        type=amqp_config.get('EXCHANGE_TYPE')
    )
    queue_name = amqp_config.get('QUEUE_NAME') or _settings.BALI_QUEUE.format(
        service_abbr
    )

    b = Queue(queue_name, exchange, channel=channel)
    with pytest.raises(amqp.exceptions.NotFound):
        b.queue_declare(passive=True)

    # 3. Launch `Product` service's handle
    handle()
    # 4. Assert `product.events` queue exists，and bind to exchange `ms.events`
    b = Queue(queue_name, exchange, channel=channel)
    assert b.queue_declare(passive=True)

    # clean
    conn.close()
