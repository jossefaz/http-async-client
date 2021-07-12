from enum import Enum


class SupportedProtocols(Enum):
    http = "http"
    https = "https"


class Methods(Enum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"