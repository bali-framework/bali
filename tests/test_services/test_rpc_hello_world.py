import pytest

from bali import Bali
from . import helloworld_rpc_service
from .protos import helloworld_pb2 as pb2
from .protos import helloworld_pb2_grpc as pb2_grpc


Bali.__clear__()

app = Bali(
    title='helloworld',
    rpc_service=helloworld_rpc_service,
)


@pytest.fixture(scope='module')
def grpc_add_to_server():
    return pb2_grpc.add_HelloworldServicer_to_server


@pytest.fixture(scope='module')
def grpc_servicer():
    return app._rpc_servicer()


@pytest.fixture(scope='module')
def grpc_stub_cls(grpc_channel):
    return pb2_grpc.HelloworldStub


def test_say_hello(grpc_stub):
    name = 'Bali'
    request = pb2.HelloRequest(name=name)
    response = grpc_stub.SayHello(request)

    assert response.message == 'Hello, %s!' % name
