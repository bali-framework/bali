from kombu import Connection, Queue, Exchange

from .event import Event
from ..core import _settings


def dispatch(event: Event, amqp_name: str = ''):
    if not amqp_name:
        amqp_name = event.amqp_name
    amqp_config = _settings.AMQP_CONFIGS.get(amqp_name, {})
    if not amqp_config:
        raise Exception('Settings not set:sub config of AMQP_CONFIGS not set')
    if 'AMQP_SERVER_ADDRESS' not in amqp_config:
        raise Exception('Settings not set: AMQP_SERVER_ADDRESS of sub config')

    routing_key = None
    exchange_type = amqp_config.get('EXCHANGE_TYPE')
    exchange = Exchange(
        name=amqp_config.get('EXCHANGE_NAME') or _settings.BALI_EXCHANGE,
        type=exchange_type
    )
    declare = [exchange]
    if exchange_type != 'fanout':
        routing_key = amqp_config.get(
            'ROUTING_KEY'
        ) or _settings.BALI_ROUTING_KEY.format(event.type)
    if amqp_config.get('QUEUE_NAME'):
        queue = Queue(
            amqp_config.get('QUEUE_NAME'),
            exchange,
            routing_key=routing_key
        )
        declare.append(queue)
    with Connection(amqp_config['AMQP_SERVER_ADDRESS']) as conn:
        # produce
        producer = conn.Producer(serializer='json')
        return producer.publish(
            event.dict(),
            exchange=exchange,
            routing_key=routing_key,
            declare=declare,
            retry=True
        )
