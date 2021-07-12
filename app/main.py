from enum import Enum
from functools import partial
from typing import Union

import httpx
import re

from dataclasses import dataclass
from nanoid import generate
import base64
import threading


class EndPointRegistry(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        cls._locker = threading.Lock()
        cls.endpoints_registry: dict[bytes, EndPoint] = {}
        cls.current = bytes()
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            with cls._locker:
                if cls.__instance is None:
                    cls.__instance = super().__call__(*args, **kwargs)
        cls.add_to_reg(**kwargs)
        return cls.__instance

    def add_to_reg(cls, **kwargs):
        port = kwargs.get("port", None)
        protocol = kwargs.get("protocol", None)
        host = kwargs.get("host", None)
        end_point = EndPoint(host, port, protocol)
        if not end_point.base_url:
            raise ValueError("EndPointRegistry error trying to add new client : host is missing")
        try:
            end_point_key = base64.b64encode(bytes(end_point.base_url, encoding='utf-8'))
            if end_point_key not in cls.endpoints_registry:
                cls.endpoints_registry[end_point_key] = end_point
            cls.current = end_point_key
        except TypeError as te:
            raise TypeError(f"Cannot encode base url to registry : {str(te)}")


class SupportedProtocols(Enum):
    http = "http"
    https = "https"


@dataclass
class EndPoint:
    host: str
    port: int
    _protocol: str

    @property
    def base_url(self) -> Union[bool, str]:
        """
        Build the base url based on the protocol, the host and the port. Only host is mandatory, others will be ignored or given default value
        :return: base url
        """
        if not self.host:
            return False
        return f"{self.protocol.value}://{self.host}:{self.port}" if self.port \
            else f"{self.protocol.value}://{self.host}"

    @property
    def protocol(self) -> SupportedProtocols:
        """
        Get the protocol if the one that was given in constructor is supported, otherwise give the default http protocol
        :return: Entry of the enum SupportedProtocols
        """
        if self._protocol in SupportedProtocols.__members__:
            return SupportedProtocols[self._protocol]
        return SupportedProtocols.http


class BaseRESTAsyncClient(metaclass=EndPointRegistry):
    def __init__(self, *, host, port=None, protocol=None):
        self._request_id = None

    @property
    def request_id(self):
        """
        Getter for the request id
        :return:
        """
        if not self._request_id:
            return None
        return str(self._request_id)

    @request_id.setter
    def request_id(self, value):
        """
        Setter for the request id
        TODO: Check if there is any pre existing request ID from the incoming request headers and generate one ONLY IF there is no
        :return: Nano ID
        """
        self._request_id = generate()

    def get_base_url(self) -> str:
        return self.endpoints_registry[self.current].base_url

    def make_url(self, url: str = ""):
        """
        Url builder based on the host base url
        :param url: relative url that will be concatenate wil the host base url
        :return: An absolute url including the protocol, the host base url, port (if any) and the relative url if any
        """
        # Ensure to remove keep only one "/" along all the url
        url = re.sub('/+', '/', url)
        # remove the first "/" at the beginning
        url = re.sub('^/', '', url)
        return f"{self.get_base_url()}/{url}"

    @classmethod
    def get_instance(cls, *, host, port=None, protocol=None) -> "partial[BaseRESTAsyncClient]":
        """
        Will return a factory (as a partial function) in order to always ensure the current endpoint is selected in the endpoints registry
        :param host: str
        :param port: int
        :param protocol: str (must be a value of the SupportedProtocols Enum
        :return:partial  function (BaseRESTAsyncClient factory)
        """
        return partial(BaseRESTAsyncClient, host=host, port=port, protocol=protocol)

    def __call__(self, *args, **kwargs):
        """
        Will trow an error that avoid BaseRESTAsyncClient to be called directly and force use the get_instance class method
        """
        raise TypeError("BaseClient cannot be called directly use get_instance class method instead")

    async def get(self, url: str = "", params:dict={}):
        async with httpx.AsyncClient() as client:
            return await client.get(self.make_url(url))
