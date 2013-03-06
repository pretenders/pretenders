class NoPortAvailableException(Exception):
    pass


class ConfigurationError(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class UnexpectedResponseStatus(Exception):
    pass


class NoRequestFound(Exception):
    pass
