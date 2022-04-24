from typing import Dict, Any

from kombu import Exchange, Queue
from pydantic import BaseModel


class Event(BaseModel):
    type: str
    payload: Dict[str, Any] = {}

    def dict(self):
        res = super().dict()
        return {
            'event_type': self.type,
            **res['payload']
        }

