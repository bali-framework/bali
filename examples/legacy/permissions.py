from bali.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self):
        return True

    def process_auth(self):
        print(self.resource)
