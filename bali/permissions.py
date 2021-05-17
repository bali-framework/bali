from pydantic import BaseModel


class BasePermission:
    """
    A base class from which all permission classes should inherit.
    """
    def __init__(self, resource):
        self.resource = resource

    def check(self):
        self.process_auth()
        return self.has_permission()

    def has_permission(self):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        self.process_auth()
        return True

    def process_auth(self):
        # self.resource.auth = BaseModel()
        pass
