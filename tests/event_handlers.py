import os

from bali import event_handler
from bali.core import _settings

amqp_uri = os.getenv('AMQP_SERVER_ADDRESS', default='amqp://127.0.0.1:5672')

_settings.AMQP_CONFIGS = {
    'default': {
        'AMQP_SERVER_ADDRESS': amqp_uri
    }
}


class EventHandler:
    @event_handler("event_type")
    def handle_event(self, event):
        print("Event handler received: ", event)
