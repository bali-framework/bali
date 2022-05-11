import socket

from kombu import Connection, Queue, connections, Exchange

from ..core import _settings

REGISTER_EVENT_CALLBACKS = []


def register_callback(event_type, callback):
    amqp_config_key = _settings.EVENT_TYPE_TO_AMQP.get(event_type, 'default')
    if not amqp_config_key:
        raise Exception(
            'Can not find key:%s at EVENT_TYPE_TO_AMQP' % amqp_config_key
        )
    amqp_config = _settings.AMQP_CONFIGS.get(amqp_config_key)
    if not amqp_config:
        raise Exception(
            'Can not find key:%s at AMQP_CONFIGS' % amqp_config_key
        )
    exchange = Exchange(
        amqp_config.get('EXCHANGE_NAME', _settings.EVENT_DEFAULT_EXCHANGE),
        type=amqp_config.get('EXCHANGE_TYPE')
    )
    queue = Queue(
        amqp_config.get('QUEUE_NAME', _settings.EVENT_DEFAULT_QUEUE),
        exchange=exchange,
        key=amqp_config.get(
            'ROUTING_KEY', _settings.EVENT_DEFAULT_ROUTING_KEY
        )
    )
    global REGISTER_EVENT_CALLBACKS
    REGISTER_EVENT_CALLBACKS.append(
        (
            queue,
            callback,
            amqp_config['AMQP_SERVER_ADDRESS'],
        )
    )


def get_connection(amqp_address):
    c1 = Connection(amqp_address)
    return connections[c1].acquire(block=True)


def handle():
    for queue, callback, amqp_address in REGISTER_EVENT_CALLBACKS:
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
    return True
