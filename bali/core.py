import locale
import os

from .application import Bali
from .cache import cache
from .db import db

DEFAULT_LC_ALL = "id_ID.UTF-8"
LC_ALL = os.environ.setdefault("LC_ALL", DEFAULT_LC_ALL)

try:
    locale.setlocale(locale.LC_ALL, LC_ALL)
except locale.Error:
    pass
