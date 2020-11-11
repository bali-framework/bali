from bali.db import db


# noinspection PyProtectedMember
def test_db_connect():
    db.connect('sqlite://')
    assert db._session is not None
