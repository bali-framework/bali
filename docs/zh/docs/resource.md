## Resource

<i>New in version 2.0.</i>

Resource’s design borrows several key concepts from the REST architectural style.

Inspired by `ViewSet` in Django REST Framework.

Actions' name according [`Standard methods` in Google API design guide](https://cloud.google.com/apis/design/standard_methods) 

### Generic HTTP/RPC Actions

Generic HTTP/RPC support actions:

|Action |Route |Method | RPC  | Description|
--- |--- | --- | --- | ---
|get |/{id} |GET |Get{Resource} |Get an existing resource matching the given id |
|list |/ |GET |List{Resource} |Get all the resources |
|create |/ |POST |Create{Resource} |Create a new resource |
|update |/{id} |PATCH |Update{Resource} |Update an existing resource matching the given id |
|delete |/{id} |DELETE |Delete{Resource} |Delete an existing resource matching the given id |

Generic Actions examples:

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

### ModelResource

<i>New in version 2.1.</i>

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
