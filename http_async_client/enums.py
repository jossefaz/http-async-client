from enum import Enum


class SupportedProtocols(Enum):
    """Contains a list of all supported protocols (currently only http and https
    Value:
        http : "http"
        https : "https"
    """
    http = "http"
    https = "https"


class Methods(Enum):
    """Contains a list of all supported HTTP Verbs
    """
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"