from concurrent import futures

import grpc


class GRPCTestBase:
    server = None
    server_class = None  # must provided in inherit class
    port = 50001

    service_target = 'localhost'  # grpc channel target address
    pb2 = None
    pb2_grpc = None

    def setup_class(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        self.pb2_grpc.add_UserServiceServicer_to_server(self.server_class(), self.server)
        self.server.add_insecure_port(f'[::]:{self.port}')
        self.server.start()

        self.service_target = f'localhost:{self.port}'

    def teardown_class(self):
        self.server.stop(None)
