from typing import Dict, Any

from pydantic import BaseModel


class Event(BaseModel):
    __amqp_name__ = 'default'

    type: str
    payload: Dict[str, Any] = {}

    @property
    def amqp_name(self):
        return self.__amqp_name__
