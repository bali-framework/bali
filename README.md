# bali

Simplify gRPC services & FastAPI 


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


## Service Mixin

```python
# import 
from bali.mixins import ServiceMixin

class Hello(hello_pb2_grpc.HelloServiceServicer, ServiceMixin):
    pass
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
