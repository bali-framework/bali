import socket
from itertools import groupby

from kombu import Connection, Queue, connections, Exchange

from ..core import _settings

REGISTER_EVENT_CALLBACKS = []


class Callback:
    def __init__(self, queue, callback, connection):
        self._queue = queue
        self._callback = callback
        self._connection = connection

    def __str__(self):
        return f'{self._connection}/{self._queue.name}'

    @property
    def connection(self):
        return self._connection

    @property
    def queue(self):
        return self._queue

    @property
    def callback(self):
        return self._callback


def register_callback(event_type, callback):
    amqp_config_keys = _settings.EVENT_TYPE_TO_AMQP.get(event_type, 'default')
    if not amqp_config_keys:
        raise Exception(
            'Can not find key:%s at EVENT_TYPE_TO_AMQP' % event_type
        )
    arr = amqp_config_keys.split(',')
    for amqp_config_key in arr:
        amqp_config = _settings.AMQP_CONFIGS.get(amqp_config_key)
        if not amqp_config:
            raise Exception(
                'Can not find key:%s at AMQP_CONFIGS' % amqp_config_key
            )
        routing_key = None
        exchange_type = amqp_config.get('EXCHANGE_TYPE')
        if exchange_type != 'fanout':
            routing_key = amqp_config.get(
                'ROUTING_KEY'
            ) or _settings.BALI_ROUTING_KEY.format(event_type)
        exchange = Exchange(
            amqp_config.get('EXCHANGE_NAME', _settings.BALI_EXCHANGE),
            type=exchange_type
        )
        queue = Queue(
            amqp_config.get('QUEUE_NAME') or
            _settings.BALI_QUEUE.format(event_type),
            exchange=exchange,
            routing_key=routing_key
        )
        global REGISTER_EVENT_CALLBACKS
        REGISTER_EVENT_CALLBACKS.append(
            Callback(queue, callback, amqp_config['AMQP_SERVER_ADDRESS'])
        )


def get_connection(amqp_address):
    c1 = Connection(amqp_address)
    return connections[c1].acquire(block=True)


def handle():
    groups = groupby(REGISTER_EVENT_CALLBACKS, key=lambda x: str(x))
    for k, items in groups:
        items = list(items)
        with get_connection(amqp_address=items[0].connection) as conn:
            with conn.Consumer(
                queues=[items[0].queue],
                accept=['json'],
                callbacks=[i.callback for i in items],
                auto_declare=True
            ) as consumer:
                try:
                    conn.drain_events(timeout=2)
                except socket.timeout:
                    pass
                except Exception as e:
                    raise e
    return True
