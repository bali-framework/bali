from typing import Dict, Any

from pydantic import BaseModel


class Event(BaseModel):
    type: str
    payload: Dict[str, Any] = {}
