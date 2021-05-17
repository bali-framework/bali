# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

import logging
from concurrent import futures

import grpc

import helloworld_pb2
import helloworld_pb2 as pb2
import helloworld_pb2_grpc
from bali.interceptors import ProcessInterceptor
from bali.mixins import ServiceMixin
from resources import GreeterResource


class Greeter(helloworld_pb2_grpc.GreeterServicer, ServiceMixin):
    def SayHello(self, request, context):
        print('Greeter.SayHello')
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)

    def GetGreeter(self, request, context):
        print('Greeter.GetGreeter')
        return GreeterResource(request, context, pb2.ItemResponse).get()

    def ListGreeter(self, request, context):
        print('Greeter.ListGreeter')
        return GreeterResource(request, context, pb2.ListResponse).list()

    def CreateGreeter(self, request, context):
        print('Greeter.CreateGreeter')
        return GreeterResource(request, context, pb2.ItemResponse).create()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ProcessInterceptor()],
    )
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Service Hello world started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
