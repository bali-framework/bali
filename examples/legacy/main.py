# noinspection PyUnresolvedReferences
import config
import grpc_server_async
from bali.core import Bali
from event_handler import EventHandler
from v1.app import router

app = Bali(
    base_settings=None,
    routers=[{
        'router': router,
        'prefix': '/v1',
    }],
    backend_cors_origins=['http://127.0.0.1'],
    rpc_service=grpc_server_async,
    event_handler=EventHandler
)
app.settings(title='legacy')

if __name__ == "__main__":
    app.start()
