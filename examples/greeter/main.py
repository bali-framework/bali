from bali import Bali, Schema, Resource
from bali.decorators import action


class Greeter(Schema):
    content: str


class GreeterResource(Resource):

    schema = Greeter

    @action()
    def get(self, pk=None):
        return {'content': f'hello, ID is {pk}'}


app = Bali()
app.register(GreeterResource)

if __name__ == "__main__":
    app.start()
