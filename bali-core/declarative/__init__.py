import collections

import humps
import pydantic
from pydantic import BaseModel, create_model

from ..decorators import action
from ..resources import Resource, GENERIC_ACTIONS

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
            if "list" in self._factory._dict_response_values:
                return self._factory._dict_response_values["list"]

            return self._factory._schema.find()

        @action()
        def create(self, *args, **kwargs):
            if "create" in self._factory._dict_response_values:
                return self._factory._dict_response_values["create"]

            raise NotImplementedError

        @action()
        def get(self, pk):
            if "get" in self._factory._dict_response_values:
                return self._factory._dict_response_values["get"]

            return self._factory._schema.find(pk)

        @action()
        def update(self, *args, **kwargs):
            if "update" in self._factory._dict_response_values:
                return self._factory._dict_response_values["update"]

            raise NotImplementedError

        @action()
        def delete(self, *args, **kwargs):
            if "delete" in self._factory._dict_response_values:
                return self._factory._dict_response_values["delete"]

            raise NotImplementedError

        type_dict = self._get_resource_type_dict(locals())

        # noinspection PyUnresolvedReferences
        return type(
            f"{humps.pascalize(self.resource_name)}Resource",
            (Resource, ),
            type_dict,
        )

    def _push_action(self, actions):
        if not isinstance(actions, list):
            actions = [actions]
        for action_name in actions:
            if action_name not in self._actions:
                self._actions.append(action_name)

    def _get_resource_type_dict(self, contexts):
        # defined resource class members
        type_dict = {
            "_factory": self,
            "schema": self._schema,
        }
        for action_name in self._actions:
            type_dict[action_name] = contexts[action_name]

        return type_dict

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

    def _clear(self):
        """Reset API values, most used in unittests"""
        self.__init__()


API = DeclarativeAPI()
