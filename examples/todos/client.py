from __future__ import print_function

import sys

import grpc

from bali.utils import MessageToDict

if __name__ == '__main__':
    sys.path.append('protos')

    import todos_pb2 as pb2
    import todos_pb2_grpc as pb2_grpc

    # Create todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        response = stub.CreateTodo(
            pb2.TodoEntity(
                text='Shopping',
                completed=False,
            )
        )
        print("Create todos: %s" % MessageToDict(response))

    # List todos
    with grpc.insecure_channel('localhost:9080') as channel:
        stub = pb2_grpc.TodosStub(channel)
        response = stub.ListTodos(pb2.ListRequest(limit=2, offset=0))
        print("List todos: %s" % MessageToDict(response))
