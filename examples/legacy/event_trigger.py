import os

from bali.core import _settings
from bali.events import Event, dispatch

amqp_uri = os.getenv('AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672')


_settings.AMQP_CONFIGS = {
    'default': {
        'AMQP_SERVER_ADDRESS': amqp_uri,
        'EXCHANGE_NAME': 'ms.events',
        'EXCHANGE_TYPE': 'fanout',
    }
}


class HelloSaidEvent(Event):
    """Hello said event"""
    type: str = 'HelloSaid'
    name: str = ''


class HiSaidEvent(Event):
    """Hi said event"""
    type: str = 'HiSaid'
    name: str = ''


def run():
    event = HelloSaidEvent(name='Jack')
    dispatch(event)
    print('Dispatched event: ', event)

    event = HiSaidEvent(name='Jerry')
    dispatch(event)
    print('Dispatched event: ', event)


if __name__ == '__main__':
    run()
