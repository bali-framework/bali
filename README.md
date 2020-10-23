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

### CONTRIBUTE

tag a version:

```bash
git tag -a v0.1.0
```

push tags to remote:

```bash
git push --tags
```
