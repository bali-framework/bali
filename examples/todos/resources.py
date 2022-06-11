from bali import ModelResource

from models import Todo


class TodoResource(ModelResource):
    model = Todo
