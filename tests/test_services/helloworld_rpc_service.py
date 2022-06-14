import sys


print('sys.path[0]: ', sys.path[0])

from .protos import helloworld_pb2 as pb2
from .protos import helloworld_pb2_grpc as pb2_grpc


class HelloworldServicer(pb2_grpc.HelloworldServicer):
    def SayHello(self, request, context):
        return pb2.HelloReply(message='Hello, %s!' % request.name)
