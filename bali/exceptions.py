class DBSetupException(Exception):
    """Raise when database not initialized"""
    def __init__(self, message='Database session not initialized'):
        self.message = message
        super().__init__(self.message)


class ReturnTypeError(Exception):
    """Resource action return type error"""
    pass


class OperatorModelError(Exception):
    """Model not provided in django-like operator"""
    pass
