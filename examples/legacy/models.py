from bali.core import db


class Item(db.BaseModel):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), default='')
