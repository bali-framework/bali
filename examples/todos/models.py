import sqlalchemy as sa
from bali import db


class Todo(db.Base):
    id = sa.Column('id', sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column('text', sa.String(100))
    completed = sa.Column('completed', sa.Boolean(), default=False)
