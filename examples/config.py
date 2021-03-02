from pydantic import BaseSettings
from bali.core import initialize


class Settings(BaseSettings):
    pass


settings = Settings()

initialize(settings)
