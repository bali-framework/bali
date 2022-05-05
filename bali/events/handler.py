import socket

from kombu import Connection, Queue, connections

from ..core import _settings

REGISTER_EVENT_CALLBACKS = {}


def register_callback(event_type, callback):
    amqp_config_key = _settings.EVENT_TO_AMQP_MAP.get(event_type)
    if not amqp_config_key:
        raise Exception(
            'Can not find key:%s at EVENT_TO_AMQP_MAP' % amqp_config_key
        )
    amqp_config = _settings.AMQP_CONFIGS.get(amqp_config_key)
    if not amqp_config:
        raise Exception(
            'Can not find key:%s at AMQP_CONFIGS' % amqp_config_key
        )
    queue = Queue(
        amqp_config['QUEUE_NAME'],
        exchange=amqp_config['EXCHANGE_NAME'],
        key=amqp_config['ROUTING_KEY']
    )
    global REGISTER_EVENT_CALLBACKS
    REGISTER_EVENT_CALLBACKS[event_type] = (
        queue, callback, amqp_config['AMQP_SERVER_ADDRESS']
    )


def get_connection(amqp_address):
    c1 = Connection(amqp_address)
    return connections[c1].acquire(block=True)


def handle():
    for queue, callback, amqp_address in REGISTER_EVENT_CALLBACKS.values():
        with get_connection(amqp_address=amqp_address) as conn:
            with conn.Consumer(
                    queues=[queue], accept=['json'], callbacks=[callback]
            ) as consumer:
                try:
                    conn.drain_events(timeout=1)
                except socket.timeout:
                    pass
                except Exception as e:
                    raise e
