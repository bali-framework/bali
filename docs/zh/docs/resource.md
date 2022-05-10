## Resource

<i>在版本 2.0. 中加入</i>

Resource的设计借鉴了REST体系结构风格的几个关键概念。

灵感来自于Django REST框架中的' ViewSet '。

Actions 命名依据 [`Standard methods` in Google API design guide](https://cloud.google.com/apis/design/standard_methods) 

### 通用 HTTP/RPC 支持操作

通用 HTTP/RPC 支持操作:

|Action |Route |Method | RPC  | Description|
--- |--- | --- | --- | ---
|get |/{id} |GET |Get{Resource} |获取与给定id匹配的现有资源 |
|list |/ |GET |List{Resource} |获取所有资源 |
|create |/ |POST |Create{Resource} |创建一个新的资源 |
|update |/{id} |PATCH |Update{Resource} |更新与给定 id 匹配的现有资源 |
|delete |/{id} |DELETE |Delete{Resource} |删除与给定 id 匹配的现有资源 |

通用示例:

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

### 用户自定义 HTTP/RPC Actions

用户自定义的 Action 还是需要使用 `@action`, 单是参数 `detail` 必须要设置.


```python
@action(detail=False)
def custom_action(self):
    pass
```

`detail` 没有默认值.
> `True` 代表 action 对应的是单个资源, url 为 '/{resources}/{id}'.
> 
> `False` 代表 action 对应的是一个资源集, url 为 '/{resources}'.


### 重写 HTTP Actions

如果默认的HTTP动作模板不能满足您的请求，您可以覆盖HTTP动作。

```python
# Get the origin router 
router = GreeterResource.as_router()
# Override the actions using the FastAPI normal way
@router.get("/")
def root():
    return {"message": "Hello World"}
```

> 更多关于 `Resource`: [GreeterResource](examples/resources/greeter.py)

### ModelResource

<i>在版本 2.1. 中新增</i>

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
