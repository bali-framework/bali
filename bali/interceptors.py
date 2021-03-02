"""
gRPC interceptors
"""
import grpc
import logging

from google.protobuf import json_format

from bali.core import db

from typing import Callable, Any
from grpc_interceptor import ServerInterceptor
from .core import _settings

logger = logging.getLogger('bali')


class ProcessInterceptor(ServerInterceptor):
    def setup(self):
        pass

    def teardown(self):
        try:
            db.remove()
        except Exception:
            pass

    @staticmethod
    def log(request, method_name, log_type):
        logger.info(
            '%s %s: %s',
            method_name,
            json_format.MessageToDict(
                request, including_default_value_fields=True, preserving_proto_field_name=True
            ),
            log_type,
        )

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
        try:
            _settings.ENABLED_RPC_LOGGING and self.log(request, method_name, 'Request')
            result = method(request, context)
            _settings.ENABLED_RPC_LOGGING and self.log(request, method_name, 'Response')
        finally:
            self.teardown()

        return result
