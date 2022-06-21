import os

from kombu import Connection, Queue

from bali import Bali
from bali.core import _settings

amqp_uri = os.getenv('AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672')


class TestBaliAppEvent:
    """Test event infrastructure ready when event handle provided"""

    title = 'app_product'
    exchange = 'ms.events'
    queue = 'app_product.events'

    def setup_class(self):
        # clear Bali singleton
        Bali.__clear__()

        # Delete RabbitMQ's ms.events exchange
        conn = Connection(amqp_uri)
        channel = conn.channel()
        channel.queue_delete(self.queue)
        channel.exchange_delete(self.exchange)

    def test_amqp_infrastructure_ready(self):
        _settings.Config.__setattr__(_settings, 'SERVER_NAME', 'app_product')
        _settings.Config.__setattr__(
            _settings, 'BALI_QUEUE', 'app_product.events'
        )
        _settings.AMQP_CONFIGS = {
            'default': {
                'AMQP_SERVER_ADDRESS': amqp_uri,
                'EXCHANGE_TYPE': 'fanout'
            }
        }

        from .event_handlers import EventHandler
        app = Bali(title='app_product', event_handler=EventHandler)

        from bali.events import handle
        handle()

        # 4. Assert `product.events` queue exists，and bind to exchange `ms.events`
        conn = Connection(amqp_uri)
        channel = conn.channel()
        b = Queue(self.queue, self.exchange, self.queue, channel=channel)
        assert b.queue_declare(passive=True)

        conn.close()
