# bali

Simplify gRPC services & FastAPI 


## Database 

```python
from bali.core import db
db.connect('DATABASE_URI')  # connect to database when app started
```


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

tag a version:

```bash
git tag -a v0.1.0
```

push tags to remote:

```bash
git push --tags
```
