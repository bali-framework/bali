"""
gRPC interceptors
"""
import grpc
from bali.core import db

from typing import Callable, Any
from grpc_interceptor import ServerInterceptor


class ProcessInterceptor(ServerInterceptor):
    def setup(self):
        pass

    def teardown(self):
        try:
            db.remove()
        except Exception:
            pass

    def intercept(
        self,
        method: Callable,
        request: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:
        """
        
        :param method:
        :param request:
        :param context:
        :param method_name:
        :return:
        """
        self.setup()
        result = method(request, context)
        self.teardown()
        return result
