import logging
import socket
import time
import traceback
from itertools import groupby

from kombu import Connection, Queue, connections, Exchange

REGISTER_EVENT_CALLBACKS = []
REGISTER_EVENT_TYPES = []

logger = logging.getLogger('bali')


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
    from ..core import _settings
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
        exchange_type = amqp_config.get('EXCHANGE_TYPE') or 'direct'
        if exchange_type != 'fanout':
            routing_key = amqp_config.get(
                'ROUTING_KEY'
            ) or _settings.BALI_ROUTING_KEY.format(event_type)
        # Fails when exchange type is different and exchange name is same
        exchange = Exchange(
            amqp_config.get(
                'EXCHANGE_NAME', f'{_settings.BALI_EXCHANGE}_{exchange_type}'
            ),
            type=exchange_type
        )
        queue_name = amqp_config.get('QUEUE_NAME')
        if not queue_name:
            if exchange_type == 'fanout':
                queue_name = _settings.BALI_QUEUE
            else:
                queue_name = f'{_settings.BALI_QUEUE}.{exchange_type}'

        queue = Queue(queue_name, exchange=exchange, routing_key=routing_key)
        global REGISTER_EVENT_CALLBACKS
        global REGISTER_EVENT_TYPES
        REGISTER_EVENT_CALLBACKS.append(
            Callback(queue, callback, amqp_config['AMQP_SERVER_ADDRESS'])
        )
        REGISTER_EVENT_TYPES.append(event_type)


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
                except:
                    logger.error(traceback.format_exc())
                    time.sleep(2)
    return True
