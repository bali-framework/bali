# bali

Simplify gRPC services & FastAPI 

## Application 

Create Application

```python
import greeter_server

# Initialized App 
app = Bali()
# Updated settings
app.settings(base_settings={'title': 'Bali App'})
```

Launch 

```bash
# lauch RPC and HTTP service 
python main.py

# lauch RPC 
python main.py --rpc

# lauch HTTP
python main.py --http
```

More usage of `Application`: [example](examples/main.py)


## Database 

```python
from bali.core import db

# connect to database when app started
# db is a sqla-wrapper instance
db.connect('DATABASE_URI')  
  
```

Declarative mode with sqla-wrapper

```python

class User(db.Model):
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...

db.create_all()

db.add(User(...))
db.commit()

todos = db.query(User).all()
```

More convenient usage, ref to [SQLA-Wrapper](https://github.com/jpsca/sqla-wrapper)


Declare models inherit from convenient base models

*BaseModel*

```python
# using BaseModel
class User(db.BaseModel):
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...
```

```python
# BaseModel's source code 

class BaseModel(db.Model):
    __abstract__ = True

    created_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_time = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = Column(Boolean(), default=True)
```

## Schema

*model_to_schema*

```python
# generate pydantic schema from models
# `User` is a db.Model or db.BaseModel instance 
from bali.schema import model_to_schema
UserSchema = model_to_schema(User)
```

## Service Mixin

```python
# import 
from bali.mixins import ServiceMixin

class Hello(hello_pb2_grpc.HelloServiceServicer, ServiceMixin):
    pass
```

## Cache

```python
from bali.core import cache

# Usage example (API)

# Read cache 
cache.get(key)

# Set cache 
cache.set(key, value, timeout=10)
```

## Utils

**dateparser**

[dateparser docs](https://dateparser.readthedocs.io/en/v1.0.0/)


## Tests

**gRPC service tests**

```python
from bali.tests import GRPCTestBase
from service.demo import demo_service, demo_pb2, demo_pb2_grpc


class TestDemoRPC(GRPCTestBase):
    server_class = demo_service.DemoService  # Provided service 

    pb2 = demo_pb2  # Provided pb2
    pb2_grpc = demo_pb2_grpc  # Provided pb2 grpc

    def setup_method(self):  # Pytest setup 
        pass

    def teardown_method(self):  # Pytest teardown
        pass

    def test_demo(self):
        pass
```

### CONTRIBUTE

**Developer Environment**

```bash
pip install -r requirements_dev.txt
``` 


**Tag a new release**

tag a version:

```bash
git tag -a v0.1.0
```

push tags to remote:

```bash
git push --tags
```
