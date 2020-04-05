class MyCartableException(Exception):
    pass


class MyCartableOperationError(MyCartableException):
    """raised if creation d'operation fail"""

    pass
