# config 

## configuration file

Configuration file is a python file location in project root directory.

```bash
todos
├── README.md
├── client.py
├── config.py   <-- configuration file
├── main.py
├── migrations
├── models.py
├── protos
├── resources.py
└── todo.sqlite
```

Todos Example project configuration file: [config.py](examples/todos/config.py)


## Multi ENV Configuration

Inspired by "Flask Web Development" (https://www.oreilly.com/library/view/flask-web-development/9781491991725/)

```python
# config.py
import humps
from pydantic import BaseSettings
from bali.environments import ENV
from bali.core import initialize


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True
    
class DevSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True
    
class TestSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True
    
class StagingSettings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///todo.sqlite'
    ENABLE_MIGRATE: bool = True


settings: Settings = humps.pascalize(ENV.name.lower()).Settings()
initialize(settings)
```

## Builtin Configuration Values

The following configuration values are used internally by Bali Application:

### ENV
What environment the app is running in. The env attribute maps to this config key.

Default: "DEV"


### SQLALCHEMY_DATABASE_URI
Database URI in SQLAlchemy schema.

Default: None
