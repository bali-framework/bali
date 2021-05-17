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
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import logging

import grpc

import helloworld_pb2
import helloworld_pb2_grpc
from bali.utils import MessageToDict, ParseDict


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
        print("Greeter client received <SayHello>: %s" % response.message)

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.GetGreeter(helloworld_pb2.GetRequest(id=3))
        print("Greeter client received <GetGreeter>: %s" % MessageToDict(response))

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        data = {
            'id': 1,
            'content': 'Greeter',
        }
        request_pb = ParseDict(
            {'data': data},
            helloworld_pb2.CreateRequest(),
            ignore_unknown_fields=True,
        )
        response = stub.CreateGreeter(request_pb)
        print("Greeter client received <CreateGreeter>: %s" % MessageToDict(response))

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.ListGreeter(helloworld_pb2.ListRequest(limit=2, offset=3))
        print("Greeter client received <ListGreeter>: %s" % MessageToDict(response))


if __name__ == '__main__':
    logging.basicConfig()
    run()
