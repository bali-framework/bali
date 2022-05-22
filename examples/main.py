# noinspection PyUnresolvedReferences
import config
# import grpc_server
import grpc_server_async
from bali.core import Bali
import event_handler
from v1.app import router
from fastapi_pagination import LimitOffsetPage, add_pagination, paginate


app = Bali(
    base_settings=None,
    routers=[{
        'router': router,
        'prefix': '/v1',
    }],
    backend_cors_origins=['http://127.0.0.1'],
    rpc_service=grpc_server_async,
    event_handler=event_handler
)
app.settings(title='Bali Example')

if __name__ == "__main__":
    app.start()
