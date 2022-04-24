from typing import Dict, Any

from kombu import Exchange, Queue
from pydantic import BaseModel


class Event(BaseModel):
    type: str
    payload: Dict[str, Any]
    exchange_name: str
    exchange_type: str = 'direct'
    queue_name: str
    routing_key: str

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.exchange = Exchange(
            self.exchange_name, self.exchange_type, durable=True
        )
        self.queue = Queue(
            self.queue_name,
            exchange=self.exchange,
            routing_key=self.routing_key
        )
