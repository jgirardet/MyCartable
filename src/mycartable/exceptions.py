class MyCartableException(Exception):
    pass


class MyCartableOperationError(MyCartableException):
    """raised if creation d'operation fail"""

    pass


class MyCartableTableauError(MyCartableException):
    """raised if creation d'operation fail"""

    pass
