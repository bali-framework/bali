from pydantic import BaseSettings, validator
from typing import Any, Dict, List, Optional, Union

from bali.core import initialize


class Settings(BaseSettings):
    SERVER_NAME: str = 'bali-test'

    DATABASE_SERVER: str = '127.0.0.1'
    DATABASE_USER: str = 'root'
    DATABASE_PASSWORD: str = '123456'
    DATABASE_NAME: str = 'bali_test'
    SQLALCHEMY_DATABASE_URI: str = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return 'mysql+pymysql://{}:{}@{}/{}'.format(
            values.get("DATABASE_USER"), values.get("DATABASE_PASSWORD"),
            values.get("DATABASE_SERVER"), values.get("DATABASE_NAME")
        )

    CACHE_ADDRESS: str = '127.0.0.1'
    CACHE_PASSWORD: str = '123456'


settings = Settings()

initialize(settings)
