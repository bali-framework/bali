"""
gRPC interceptors
"""
import grpc
import logging

from google.protobuf import json_format

from bali.core import db

from typing import Callable, Any
from grpc.aio import ServerInterceptor
from ..core import _settings

logger = logging.getLogger('bali')


class ProcessInterceptor(ServerInterceptor):
    def setup(self):
        pass

    def teardown(self):
        try:
            db.s.remove()
        except Exception:
            pass

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
        self.setup()
        try:
            result = await continuation(handler_call_details)
        finally:
            self.teardown()

        return result
