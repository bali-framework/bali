"""
Bali ModelResource
"""
from collections import OrderedDict

from .resource import Resource

__all__ = ['ModelResource']


class ModelResource(Resource):
    """
    Generic Actions is get, list, create, update, delete
    """

    # Resource's name, should automatic recognition is not provided
    name = None

    schema = None
    filters = []
    permission_classes = []

    _actions = OrderedDict()
