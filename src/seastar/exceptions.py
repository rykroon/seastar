class SeastarException(Exception):
    pass


class NonWebFunction(SeastarException):
    pass


class NotRawHttp(SeastarException):
    pass
