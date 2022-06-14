# Todos Example

> Provide both HTTP and gRPC service to manage your todo list.
> 
> List / Create / Update / Get / Delete in RESTful style
> 

### Launch Todos Service

```bash
# Create database schema in shell
# `db` is in shell context 
python main.py --shell
>>> db.create_all()

# launch http & rpc 
python main.py --http 
python main.py --rpc
```

## Interact with OpenAPI 
Open http://127.0.0.1:8000/docs in browser. 

## Interact with cURL

### Make http requests

```bash
# Create request
curl -X 'POST' \
  'http://127.0.0.1:8000/todos' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "shopping",
  "completed": false
}'
# Create response
{
  "id": 2,
  "text": "string",
  "completed": true
}


# List request
curl -X 'GET' \
  'http://127.0.0.1:8000/todos?limit=50&offset=0' \
  -H 'accept: application/json'
# List response
{
  "items": [
    {
      "id": 0,
      "text": "string",
      "completed": true
    },
    {
      "id": 1,
      "text": "string",
      "completed": true
    },
    {
      "id": 2,
      "text": "string",
      "completed": true
    }
  ],
  "total": 3,
  "limit": 50,
  "offset": 0
}
```

### Make rpc requests

```bash
python client.py

# Execute response
List todos: {'data': [{'id': 0, 'text': 'string', 'completed': True}, {'id': 1, 'text': 'string', 'completed': True}], 'count': 26}
Create todos: {'data': {'id': 26, 'text': 'Shopping', 'completed': False}}
Get todos: {'data': {'id': 26, 'text': 'Shopping', 'completed': False}}
Update todos: {'data': {'id': 26, 'text': 'Shopping Today', 'completed': True}}
Delete todos: {'result': True}
```
