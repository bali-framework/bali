from pydantic import BaseSettings
from bali import db


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True


settings: Settings = Settings()
db.connect(settings.SQLALCHEMY_DATABASE_URI)
db.create_all()
