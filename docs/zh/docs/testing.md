# Testing

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
