import collections
import uuid

import humps
import pydantic

from pydantic import BaseModel, create_model
from ..resources import Resource, ModelResource, GENERIC_ACTIONS
from ..decorators import action

__all__ = ["API"]


class ResourceFactory:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self._schema = None
        self._actions = []

        # dict response values store
        #
        # for example:
        #   ```python
        #   API("Greeter").get({'hello': 'world'})
        #   ```
        # it will stored in `self._dict_response_values`
        #   ```python
        #   {
        #       "get": {'hello': 'world'}
        #   }
        #   ```
        self._dict_response_values = {}

    def __call__(self, *args, **kwargs):

        @action()
        def list(self, *args, **kwargs):
            if 'list' in self._factory._dict_response_values:
                return self._factory._dict_response_values['list']

            return self._factory._schema.find()

        @action()
        def get(self, pk):
            if 'get' in self._factory._dict_response_values:
                return self._factory._dict_response_values['get']

            return self._factory._schema.find(pk)

        # noinspection PyUnresolvedReferences
        return type(
            f"{humps.pascalize(self.resource_name)}Resource",
            (Resource, ),
            {
                "_factory": self,
                "schema": self._schema,
                "list": list,
                "get": get,
            },
        )

    def _push_action(self, actions):
        if not isinstance(actions, list):
            actions = [actions]
        for action in actions:
            if action not in self._actions:
                self._actions.append(action)

    def schema(self, *args, **kwargs):
        """Declare schema

        if first argument is Pydantic, means schema is the Pydantic model

        :param args:
        :param kwargs:
        :return:
        """
        if args and isinstance(args[0], pydantic.main.ModelMetaclass):
            self._schema = args[0]
        return self

    def all(self, *args, **kwargs):
        self._push_action(GENERIC_ACTIONS)
        return self

    def list(self, *args, **kwargs):
        response = args[0]

        if isinstance(response, list):
            response = response[0]

        if isinstance(response, dict):
            # noinspection PyUnresolvedReferences
            schema_name = f"{humps.pascalize(self.resource_name)}Schema"
            self._schema = create_model(schema_name, **response)

            self._dict_response_values.update(list=args[0])

        self._push_action("list")

        return self

    def create(self, func):
        self._push_action("create")
        return self

    def get(self, *args, **kwargs):
        response = args[0]

        if isinstance(response, list):
            response = response[0]

        if isinstance(response, dict):
            # noinspection PyUnresolvedReferences
            schema_name = f"{humps.pascalize(self.resource_name)}Schema"
            self._schema = create_model(schema_name, **response)

            self._dict_response_values.update(get=args[0])

        self._push_action("get")
        return self

    def update(self, func):
        self._push_action("update")
        return self

    def delete(self, func):
        self._push_action("delete")
        return self


class ModelSchema(BaseModel):
    """Declarative model schema

    Expected support in-memory/SQLAlchemy/Mongo backends

    """
    _storage = collections.OrderedDict()  # in-memory storage

    @classmethod
    def push(cls, id=None, **kwargs):
        """When condition provided, execute update, otherwise create"""
        if not id:
            if len(cls._storage) <= 0:
                next_id = 1
            else:
                next_id = cls._storage.keys()[-1] + 1
            kwargs.update(id=next_id)
            cls._storage[next_id] = kwargs

        kwargs.update(id=id)
        cls._storage[id] = kwargs
        return kwargs

    @classmethod
    def pop(cls, id):
        del cls._storage[id]
        return id

    @classmethod
    def find(cls, id=None):
        if not id:
            return [v for k, v in cls._storage.items()][:50]
        return cls._storage[id]


class DeclarativeAPI:
    def __init__(self):
        self.resources_factories = []
        self.schema = ModelSchema

    def __call__(self, *args, **kwargs):
        return self.define(args[0])

    def define(self, resource_name):
        resource_factory = ResourceFactory(resource_name)
        self.resources_factories.append(resource_factory)
        return resource_factory


API = DeclarativeAPI()
