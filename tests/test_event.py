import os

from bali.core import _settings
from bali.decorators import event_handler
from bali.events import Event, dispatch, handle

_settings.AMQP_CONFIGS = {
    'default':
        {
            'AMQP_SERVER_ADDRESS': 'amqp://192.168.99.100:5672',
            'EXCHANGE_NAME': 'test_exchange',
            'QUEUE_NAME': 'test_queue',
            'ROUTING_KEY': 'test_routing_key'
        }
}
_settings.EVENT_TYPE_TO_AMQP = {
    'test0': 'default',
    'test1': 'default'
}


def test_event_dispatch():
    _settings.AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS': 'amqp://192.168.99.100:5672',
                'EXCHANGE_NAME': 'test_exchange',
                'QUEUE_NAME': 'test_queue',
                'ROUTING_KEY': 'test_routing_key'
            }
    }
    for i in range(10):
        event = Event(type='test0', payload={'hello': 'world'})
        assert dispatch(event)
    for i in range(100):
        event = Event(type='test1', payload={'hello': 'world'})
        assert dispatch(event)


@event_handler(event_type='test0')
def call_test0(event):
    print('test0 received:', event)
    print(os.path.basename('aaa.txt'))


@event_handler(event_type='test1')
def call_test1(event):
    print('test1 received:', event)
    print(os.path.basename('aaa.txt'))


def test_event_handler(mocker):
    _settings.AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS': 'amqp://192.168.99.100:5672',
                'EXCHANGE_NAME': 'test_exchange',
                'QUEUE_NAME': 'test_queue',
                'ROUTING_KEY': 'test_routing_key'
            }
    }
    _settings.EVENT_TYPE_TO_AMQP = {
        'test0': 'default',
        'test1': 'default'
    }
    mocker.patch('os.path.basename')
    handle()
    os.path.basename.assert_called_with('aaa.txt')
