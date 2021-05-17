# bali

Simplify gRPC services & FastAPI

## Install

```
pip install bali-core
```

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
from bali.schemas import model_to_schema
UserSchema = model_to_schema(User)
```

## Resource

<i>New in version 2.0.</i>

Resource’s design borrows several key concepts from the REST architectural style.

Inspired by `ViewSet` in Django REST Framework.

### Generic HTTP/RPC Actions

Generic HTTP/RPC support actions:

|Action |Route |Method | RPC  | Description|
--- |--- | --- | --- | ---
|get |/{id} |GET |Get{Resource} |Get an existing resource matching the given id |
|list |/ |GET |List{Resource} |Get all the resources |
|create |/ |GET |Create{Resource} |Create a new resource |
|update |/{id} |PATCH |Update{Resource} |Update an existing resource matching the given id |
|delete |/{id} |DELETE |Delete{Resource} |Delete an existing resource matching the given id |

Generic Actions examples:

```python

# 1. import `Resource` base class
from bali.resource import Resource


# 2. implementation actions inherited from Resource

class GreeterResource(Resource):

    schema = Greeter

    @action()
    def get(self, pk=None):
        return [g for g in GREETERS if g.get('id') == pk][0]

    @action()
    def list(self, schema_in: ListRequest):
        return GREETERS[:schema_in.limit]

    @action()
    def create(self, schema_in: schema):
        return {'id': schema_in.id, 'content': schema_in.content}

    @action()
    def update(self, schema_in: schema, pk=None):
        return {'id': pk, 'content': schema_in.content}

    @action()
    def delete(self, pk=None):
        return {'result': True}

```


### Custom HTTP/RPC Actions

Custom actions also decorated by `@action`, but `detail` signature is required.

```python
@action(detail=False)
def custom_action(self):
    pass
```

`detail` has no default value.
> `True` means action to single resource, url path is '/{resources}/{id}'.
> 
> `False` means action set of resources, url path is '/{resources}'.
> 

### Override HTTP Actions

If the default HTTP action template is not satisfied your request, you can override HTTP actions.

```python
# Get the origin router 
router = GreeterResource.as_router()

# Override the actions using the FastAPI normal way
@router.get("/")
def root():
    return {"message": "Hello World"}
```

> More usage of `Resource`: [GreeterResource](examples/resources/greeter.py)


## Service Mixin

```python
# import 
from bali.mixins import ServiceMixin

class Hello(hello_pb2_grpc.HelloServiceServicer, ServiceMixin):
    pass
```

## Cache

### Cache API

```python
from bali.core import cache

# Usage example (API)

# Read cache 
cache.get(key)

# Set cache 
cache.set(key, value, timeout=10)
```

### cache memoize

```python
# Import the cache_memoize from bali core 
from bali.core import cache_memoize

# Attach decorator to cacheable function with a timeout of 100 seconds.
@cache_memoize(100)
def expensive_function(start, end):
    return random.randint(start, end)
```

## Utils

**dateparser** 

[dateparser docs](https://dateparser.readthedocs.io/en/v1.0.0/)

**MessageToDict/ParseDict**

Optimized MessageToDict/ParseDict from `google.protobuf.js_format`

```python
from bali.utils import MessageToDict, ParseDict
```

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

## CONTRIBUTE

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
