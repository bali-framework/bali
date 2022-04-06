<p align="center">
  <img src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/bali.png" alt='bali framework' />
</p>
<p align="center">
    <em>🏝 Simplify Cloud Native Microservices development base on FastAPI and gRPC.</em>
</p>

<p align="center">
    <a href="https://pepy.tech/project/bali-core">
        <img src="https://pepy.tech/badge/bali-core" />
    </a>
    <a href="https://pypi.org/project/bali-core/">
        <img src="https://img.shields.io/pypi/v/bali-core" />
    </a>
</p>

---

**Documentation**: [https://bali-framework.github.io/bali/docs/zh](https://bali-framework.github.io/bali/docs/zh)

---

# Bali

简化基于 FastAPI 和 gRPC 的云原生微服务开发。如果你想让你的项目同时支持 HTTP 和 gRpc ,那么 Bali 可以帮助你很轻松的完成。 

Bali 的特性：
* 项目结构简单。
* 融合了 `SQLAlchemy` 并提供了 model 生成的方法。
* 提供了工具类转换 model 成为 Pydantic 模式.
* 支持 GZip 解压缩.
* 🍻 **Resource** 层处理对外服务即支持 HTTP 又支持 gRpc

## 谁在使用 Bali

<a href="https://www.360shuke.com/">
    <img width="200" src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/cases/qfin.png" />
</a>

## 依赖

    1. Python 3.8+
    2. FastAPI 0.63+
    3. grpcio>=1.32.0,<1.42

## 安装

```bash
pip install bali-core
```

## 项目结构



## 应用 

创建 Application

```python
import greeter_server

# 初始化 App 
app = Bali()
# Updated settings
app.settings(base_settings={'title': 'Bali App'})
```

启动服务

```bash
# lauch RPC 
python main.py --rpc

# lauch HTTP
python main.py --http
```

更多示例：[example](examples/main.py)


## Database 

### 连接数据库

```python
from bali.core import db

# app 启动后连接数据库
# db is a sqla-wrapper instance
db.connect('DATABASE_URI')  
  
```

### 定义一个 Model

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

更多示例： [SQLA-Wrapper](https://github.com/jpsca/sqla-wrapper)


### 通过继承 BaseModel 定义 Model

*BaseModel*

```python
# using BaseModel
class User(db.BaseModel):
    __tablename__ "users"
    id = db.Column(db.Integer, primary_key=True)
    ...
```

```python
# BaseModel 的源码

class BaseModel(db.Model):
    __abstract__ = True

    created_time = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_time = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = Column(Boolean(), default=True)
```

### 事务

默认情况下，事务是自动提交的, 当使用了 `db.transaction` 上下文后不在自动提交. 

```python
with db.transaction():
    item = Item.create(name='test1')
```

### Operators

Operators 提供 `get_filters_expr` 可以将字典类型的查询条件翻译成 SQLAlchemy 的查询表达式.  

```python
from bali.db.operators import get_filters_expr
from models import User

users = User.query().filter(*get_filters_expr(User, **filters)).all()
```

## Schema

*model 转成 schema*

```python
# generate pydantic schema from models
# `User` is a db.Model or db.BaseModel instance 
from bali.schemas import model_to_schema
UserSchema = model_to_schema(User)
```

## Resource

<i>2.0 中新特性</i>

Resource 的设计借鉴了 REST 体系结构风格中的几个关键概念。

受 Django REST 框架中的 ViewSet 启发

Actions 名称参考： [`Standard methods` in Google API design guide](https://cloud.google.com/apis/design/standard_methods) 

### 通常的 Actions

|Action |Route |Method | RPC  | Description|
--- |--- | --- | --- | ---
|get |/{id} |GET |Get{Resource} |Get an existing resource matching the given id |
|list |/ |GET |List{Resource} |Get all the resources |
|create |/ |POST |Create{Resource} |Create a new resource |
|update |/{id} |PATCH |Update{Resource} |Update an existing resource matching the given id |
|delete |/{id} |DELETE |Delete{Resource} |Delete an existing resource matching the given id |

Actions 示例:

```python

# 1. import `Resource` base class
from bali.resources import Resource


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
        return {'id': pk, 'result': True}  # using `id` instand of `result`

```


### 用户自定义的 Actions

用户自定义的 Action 需要使用 `@action` 装饰器, 并且必须设置 `detail` 参数.

```python
@action(detail=False)
def custom_action(self):
    pass
```

`detail` 没有默认值.
> `True` 代表对应的是一个单一的资源, url 通常是 '/{resources}/{id}'.
> 
> `False` 代表对应的是一个资源的集合, url 通常是 '/{resources}'.
> 

### 重载 HTTP Actions

如果默认的 HTTP Action 无法满足你的需求, 你可以重载它.

```python
# Get the origin router 
router = GreeterResource.as_router()

# Override the actions using the FastAPI normal way
@router.get("/")
def root():
    return {"message": "Hello World"}
```

> More usage of `Resource`: [GreeterResource](examples/resources/greeter.py)


### ModelResource

<i> 2.1 中的新特性</i>

```python
class UserResource(ModelResource):
    model = User
    schema = UserSchema
    filters = [
        {'username': str},
        {'age': Optional[str]},
    ]  # yapf: disable
    permission_classes = [IsAuthenticated]
```


## Service Mixin

```python
# import 
from bali.mixins import ServiceMixin

class Hello(hello_pb2_grpc.HelloServiceServicer, ServiceMixin):
    pass
```

## 缓存

### 缓存示例

```python
from bali.core import cache

# Usage example (API)

# Read cache 
cache.get(key)

# Set cache 
cache.set(key, value, timeout=10)
```

### 装饰器 cache_memoize 

```python
# Import the cache_memoize from bali core 
from bali.core import cache_memoize

# 设置 100 秒的缓存过期时间
@cache_memoize(100)
def expensive_function(start, end):
    return random.randint(start, end)
```

## 工具类

**dateparser** 

[dateparser docs](https://dateparser.readthedocs.io/en/v1.0.0/)

**MessageToDict/ParseDict**

Optimized MessageToDict/ParseDict from `google.protobuf.js_format`

```python
from bali.utils import MessageToDict, ParseDict
```

## 测试

**gRPC 测试示例**

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

## Related Projects

[![bali-cli](https://github-readme-stats.vercel.app/api/pin/?username=JoshYuJump&repo=bali-cli)](https://github.com/JoshYuJump/bali-cli)
[![cookiecutter-bali](https://github-readme-stats.vercel.app/api/pin/?username=Ed-XCF&repo=cookiecutter-bali)](https://github.com/Ed-XCF/cookiecutter-bali)
