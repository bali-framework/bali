# noinspection PyUnresolvedReferences
import config
import greeter_server
from bali.core import Bali
from v1.app import router
from fastapi_pagination import LimitOffsetPage, add_pagination, paginate


app = Bali(
    base_settings=None,
    routers=[{
        'router': router,
        'prefix': '/v1',
    }],
    backend_cors_origins=['http://127.0.0.1'],
    rpc_service=greeter_server,
)
app.settings(title='Bali Example')

if __name__ == "__main__":
    app.start()
