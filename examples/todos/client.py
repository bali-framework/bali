from __future__ import print_function

import sys

import grpc

from bali.utils import MessageToDict, ParseDict

if __name__ == '__main__':
    sys.path.append('protos')

    import todos_pb2 as pb2
    import todos_pb2_grpc as pb2_grpc

    pk = 0

    # List todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        response = stub.ListTodos(pb2.ListRequest(limit=2, offset=0))
        print("List todos: %s" % MessageToDict(response))

    # Create todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        todo = {
            'text': 'Shopping',
            'completed': False,
        }
        request = ParseDict({'data': todo}, pb2.CreateRequest())
        response = stub.CreateTodo(request)
        print("Create todos: %s" % MessageToDict(response))
        pk = MessageToDict(response).get('data').get('id')

    # Get todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        request = ParseDict({'id': pk}, pb2.GetRequest())
        response = stub.GetTodo(request)
        print("Get todos: %s" % MessageToDict(response))

    # Update todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        todo = {
            'text': 'Shopping Today',
            'completed': True,
        }
        request = ParseDict({'id': pk, 'data': todo}, pb2.UpdateRequest())
        response = stub.UpdateTodo(request)
        print("Update todos: %s" % MessageToDict(response))

    # Delete todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        request = ParseDict({'id': pk}, pb2.DeleteRequest())
        response = stub.DeleteTodo(request)
        print("Delete todos: %s" % MessageToDict(response))
