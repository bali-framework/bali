import os

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
                'HELLO_WORLD2',
            'QUEUE_NAME':
                'HELLO_QUEUE',
            # 'ROUTING_KEY': 'QUEUE3',
            'EXCHANGE_TYPE':
                'fanout'
        }
}
_settings.EVENT_TYPE_TO_AMQP = {'test0': 'default', 'test1': 'default'}


def test_event_dispatch():
    for i in range(100):
        event = Event(type='test0', payload={'hello': 'world2222222'})
        assert dispatch(event)
    for i in range(100):
        event = Event(type='test1', payload={'hello': 'world1111111'})
        assert dispatch(event)


@event_handler(event_type='test0')
def call_test0(event):
    print('test0 received:', event)
    print(os.path.dirname('bbb.txt'))


@event_handler(event_type='test1')
def call_test1(event):
    print('test1 received:', event)
    print(os.path.basename('aaa.txt'))


def test_event_handler(mocker):
    mocker.patch('os.path.basename')
    mocker.patch('os.path.dirname')
    handle()
    os.path.basename.assert_called_with('aaa.txt')
    os.path.dirname.assert_called_with('bbb.txt')
