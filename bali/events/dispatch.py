from kombu import Connection, Exchange, Queue

from .event import Event
from ..core import _settings


def dispatch(event: Event, app_name: str = 'default'):
    amqp_config = _settings.AMQP_CONFIGS.get(app_name, {})
    if not amqp_config:
        raise Exception('Settings not set:sub config of AMQP_CONFIGS not set')
    if 'AMQP_SERVER_ADDRESS' not in amqp_config:
        raise Exception('Settings not set: AMQP_SERVER_ADDRESS of sub config')
    routing_key = amqp_config.get('ROUTING_KEY', 'default')
    exchange = Exchange(
        amqp_config.get('EXCHANGE_NAME', 'default'), type='direct'
    )
    queue = Queue(
        amqp_config.get('QUEUE_NAME', 'default'),
        exchange,
        routing_key=routing_key
    )
    with Connection(amqp_config['AMQP_SERVER_ADDRESS']) as conn:
        # produce
        producer = conn.Producer(serializer='json')
        return producer.publish(
            event.dict(),
            exchange=exchange,
            routing_key=routing_key,
            declare=[queue],
            retry=True
        )
