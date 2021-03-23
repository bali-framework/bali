import asyncio
import inspect
import json
from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    Type,
    Union,
)

from fastapi import APIRouter as FastAPIRouter
from fastapi import params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    solve_dependencies,
)
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.exceptions import RequestValidationError
from fastapi.routing import run_endpoint_function, serialize_response
from pydantic.error_wrappers import ErrorWrapper
from pydantic.fields import ModelField
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount as Mount  # noqa

from bali.core import db
from .application import GzipRoute


@contextmanager
def session_persist(session):
    yield
    session and session.remove()


def get_request_handler(
    dependant: Dependant,
    body_field: Optional[ModelField] = None,
    status_code: int = 200,
    response_class: Union[Type[Response], DefaultPlaceholder] = Default(JSONResponse),
    response_field: Optional[ModelField] = None,
    response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    dependency_overrides_provider: Optional[Any] = None,
) -> Callable[[Request], Coroutine[Any, Any, Response]]:
    assert dependant.call is not None, "dependant.call must be a function"
    is_coroutine = asyncio.iscoroutinefunction(dependant.call)
    is_body_form = body_field and isinstance(body_field.field_info, params.Form)
    if isinstance(response_class, DefaultPlaceholder):
        actual_response_class: Type[Response] = response_class.value
    else:
        actual_response_class = response_class

    async def app(request: Request) -> Response:
        try:
            body = None
            if body_field:
                if is_body_form:
                    body = await request.form()
                else:
                    body_bytes = await request.body()
                    if body_bytes:
                        body = await request.json()
        except json.JSONDecodeError as e:
            raise RequestValidationError([ErrorWrapper(e, ("body", e.pos))], body=e.doc)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="There was an error parsing the body"
            ) from e
        solved_result = await solve_dependencies(
            request=request,
            dependant=dependant,
            body=body,
            dependency_overrides_provider=dependency_overrides_provider,
        )
        values, errors, background_tasks, sub_response, _ = solved_result
        if errors:
            raise RequestValidationError(errors, body=body)
        else:
            endpoint_return = await run_endpoint_function(
                dependant=dependant, values=values, is_coroutine=is_coroutine
            )
            _session = None
            if isinstance(endpoint_return, tuple):
                raw_response, _session = endpoint_return
            else:
                raw_response = endpoint_return

            with session_persist(_session):
                if isinstance(raw_response, Response):
                    if raw_response.background is None:
                        raw_response.background = background_tasks
                    return raw_response
                response_data = await serialize_response(
                    field=response_field,
                    response_content=raw_response,
                    include=response_model_include,
                    exclude=response_model_exclude,
                    by_alias=response_model_by_alias,
                    exclude_unset=response_model_exclude_unset,
                    exclude_defaults=response_model_exclude_defaults,
                    exclude_none=response_model_exclude_none,
                    is_coroutine=is_coroutine,
                )
                response = actual_response_class(
                    content=response_data,
                    status_code=status_code,
                    background=background_tasks,  # type: ignore # in Starlette
                )
                response.headers.raw.extend(sub_response.headers.raw)
                if sub_response.status_code:
                    response.status_code = sub_response.status_code
                return response

    return app


class APIRoute(GzipRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # inject sqlalchemy scope session remove to endpoint
        if not inspect.iscoroutinefunction(self.dependant.call):
            self.dependant.call = self._inject_scoped_session_clear(self.dependant.call)

    @staticmethod
    def _inject_scoped_session_clear(endpoint: callable):
        def injected_endpoint(*args, **kwargs):
            try:
                raw_response = endpoint(*args, **kwargs)
            except Exception:
                db.remove()
                raise

            # noinspection PyProtectedMember
            return raw_response, db._session._session

        return injected_endpoint

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        return get_request_handler(
            dependant=self.dependant,
            body_field=self.body_field,
            status_code=self.status_code,
            response_class=self.response_class,
            response_field=self.secure_cloned_response_field,
            response_model_include=self.response_model_include,
            response_model_exclude=self.response_model_exclude,
            response_model_by_alias=self.response_model_by_alias,
            response_model_exclude_unset=self.response_model_exclude_unset,
            response_model_exclude_defaults=self.response_model_exclude_defaults,
            response_model_exclude_none=self.response_model_exclude_none,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )


class APIRouter(FastAPIRouter):
    def add_api_route(self, *args, **kwargs):
        return super().add_api_route(*args, route_class_override=APIRoute, **kwargs)
