from contextlib import contextmanager

from .connection import db
from .models import context_auto_commit


@contextmanager
def transaction():
    token = context_auto_commit.set(False)
    yield
    context_auto_commit.reset(token)
    db.commit()
