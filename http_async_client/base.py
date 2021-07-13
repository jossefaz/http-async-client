from functools import partial
from typing import Union, Dict, Optional
from http_async_client.enums import SupportedProtocols, Methods
import httpx
import re
from dataclasses import dataclass
from httpx._types import RequestContent, URLTypes, RequestData, RequestFiles, QueryParamTypes, HeaderTypes, CookieTypes
from nanoid import generate
import base64
import threading
from httpx import Request


class EndPointRegistry(type):
    """This Class is a singleton that inherits from the `type` class, in order to provide it as a metaclass to other classes

    This class is the core of the HTTP client that differs from others client, because it will allow to manage different
    domains within the same class

    This is very useful for example if you need to send request to different third party APIS and you want to follow the
    way of that request with a same request ID.

    With this class you can keep a domain registry. Every new domain will be registered to this class. On each new call,
    it will check if the domain exists in the registry and if not il will
    create and entry for it. Afterward it will set this domain as the current domain.
    """

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        cls._locker = threading.Lock()
        cls.endpoints_registry: Dict[bytes, EndPoint] = {}
        cls.current = bytes()
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        """
        Instantiate the Singleton using the thread library in order to guarantee only one instance !

        Arguments:
            host: string, the domain's host
            port: int : Optional
            protocol : string, must be a member of the SupportedProtocol Enum

        Returns:
            cls.__instance : EndPointRegistry instance
        """
        if cls.__instance is None:
            with cls._locker:
                if cls.__instance is None:
                    cls.__instance = super().__call__(*args, **kwargs)
        # On each call : add to registry (if it is already in the reg, it wont be added but only defined as current)
        cls.add_to_reg(**kwargs)
        return cls.__instance

    def add_to_reg(cls, **kwargs):
        """Method that will create and eventually add a class EndPoint instance object and will add it to the registry if its base64 url is not present in it
        In that way, if there is the same origin with two different ports, it will be two different entry in the registry
        Arguments:
            host: string, the domain's host
            port: int : Optional
            protocol : string, must be a member of the SupportedProtocol Enum

        """
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


@dataclass
class EndPoint:
    host: str
    port: int
    _protocol: str

    @property
    def base_url(self) -> Union[bool, str]:
        """Build the base url based on the protocol, the host and the port. Only host is mandatory, others will be ignored or given default value.
        Returns:
            The Base URL following this template "{protocol}://{host}:{port}"
        """
        if not self.host:
            return False
        return f"{self.protocol.value}://{self.host}:{self.port}" if self.port \
            else f"{self.protocol.value}://{self.host}"

    @property
    def protocol(self) -> SupportedProtocols:
        """Get the protocol if the one that was given in constructor is supported, otherwise give the default http protocol
        Returns:
             Entry of the enum SupportedProtocols
        """
        if self._protocol in SupportedProtocols.__members__:
            return SupportedProtocols[self._protocol]
        return SupportedProtocols.http


class BaseRESTAsyncClient(metaclass=EndPointRegistry):
    def __init__(self, *, host, port=None, protocol=None):
        self._request_id = None

    @classmethod
    def get_instance(cls, *, host: str, port: Optional[int] = None,
                     protocol: Optional[str] = None) -> "partial[BaseRESTAsyncClient]":
        """Will return a factory (as a partial function) in order to always ensure the current endpoint is selected in the endpoints registry
        Arguments:
            host: domain's host
            port: listening port
            protocol: Network Protocol (must be a value of the SupportedProtocols Enum)
        Returns:
            partial  function (BaseRESTAsyncClient factory)
        Example:
            ```python
             client = BaseRESTAsyncClient.get_instance("example.com", 8080, "https")
            ```
        """
        return partial(BaseRESTAsyncClient, host=host, port=port, protocol=protocol)

    @property
    def request_id(self) -> str:
        """Getter for the request id
        Returns:
            nanoid: uid of the current request
        """
        if not self._request_id:
            return None
        return str(self._request_id)

    @request_id.setter
    def request_id(self, req_id):
        """Setter for the request id
        Arguments:
            req_id : UID (nanoid) of the request
        Todo:
            * Check if there is any pre existing request ID from the incoming request headers and generate one ONLY IF there is no
        """
        self._request_id = generate()

    def get_base_url(self) -> str:
        return self.endpoints_registry[self.current].base_url

    def make_url(self, url: str = ""):
        """Url builder based on the host base url
        Arguments:
            url: relative url that will be concatenate wil the host base url
        Returns:
            string: An absolute url including the protocol, the host base url, port (if any) and the relative url if any
        """
        # Ensure to remove keep only one "/" along all the url
        url = re.sub('/+', '/', url)
        # remove the first "/" at the beginning
        url = re.sub('^/', '', url)
        return f"{self.get_base_url()}/{url}"

    async def _send_request(self, req: Request):
        """
        Arguments:
            req: a Request ([httpx](https://www.python-httpx.org/api/#request) type)
        Returns:
            coroutine: handle the HTTP response by awaiting it
        """
        async with httpx.AsyncClient() as client:
            return await client.send(req)

    async def get(self,
                  url: URLTypes = "",
                  *,
                  params: QueryParamTypes = None,
                  headers: HeaderTypes = None,
                  cookies: CookieTypes = None):
        """Prepare an HTTP `GET` request and send it asynchronously

        Arguments:
            url: Relative URL (from the base URL)
            params: Query string
            headers: HTTP Headers (Key Value)
            cookies: HTTP Cookies
        Returns:
            coroutine : result of the `_send_request` method. It need to be awaited in order to get the HTTP response
        """
        request = Request(Methods.get.value, self.make_url(url), params=params, headers=headers, cookies=cookies)
        return await self._send_request(request)

    async def post(self,
                   url: URLTypes = "",
                   *,
                   headers: HeaderTypes = None,
                   cookies: CookieTypes = None,
                   content: RequestContent = None,
                   data: RequestData = None,
                   files: RequestFiles = None):
        """Prepare an HTTP `POST` request and send it asynchronously

        Arguments:
           url: Relative URL (from the base URL)
           headers: HTTP Headers (Key Value)
           cookies: HTTP Cookies
           data: JSON, Files, Form,
           content: All contents that are NOT one of : Form encoded, Multipart files, JSON. Could be use for text or binaries
           files: Blob stream
        Returns:
            coroutine : result of the `_send_request` method. It need to be awaited in order to get the HTTP response
        """
        request = Request(Methods.post.value, self.make_url(url),
                          content=content,
                          data=data,
                          files=files,
                          headers=headers,
                          cookies=cookies)
        return await self._send_request(request)

    async def put(self,
                  url: URLTypes = "",
                  *,
                  headers: HeaderTypes = None,
                  cookies: CookieTypes = None,
                  data: RequestData = None):
        """Prepare an HTTP `PUT` request and send it asynchronously

        Arguments:
           url: Relative URL (from the base URL)
           headers: HTTP Headers (Key Value)
           cookies: HTTP Cookies
           data: JSON, Files, Form,
        Returns:
            coroutine : result of the `_send_request` method. It need to be awaited in order to get the HTTP response
        """
        request = Request(Methods.put.value, self.make_url(url),
                          data=data,
                          headers=headers,
                          cookies=cookies)

        return await self._send_request(request)

    async def patch(self,
                    url: URLTypes = "",
                    *,
                    headers: HeaderTypes = None,
                    cookies: CookieTypes = None,
                    data: RequestData = None):
        """Prepare an HTTP `PATCH` request and send it asynchronously

        Arguments:
           url: Relative URL (from the base URL)
           headers: HTTP Headers (Key Value)
           cookies: HTTP Cookies
           data: JSON, Files, Form,
        Returns:
            coroutine : result of the `_send_request` method. It need to be awaited in order to get the HTTP response
        """
        request = Request(Methods.patch.value, self.make_url(url),
                          data=data,
                          headers=headers,
                          cookies=cookies)
        return await self._send_request(request)

    async def delete(self,
                     url: URLTypes = "",
                     *,
                     params: QueryParamTypes = None,
                     headers: HeaderTypes = None,
                     cookies: CookieTypes = None):
        """Prepare an HTTP `DELETE` request and send it asynchronously

        Arguments:
            url: Relative URL (from the base URL)
            params: Query string
            headers: HTTP Headers (Key Value)
            cookies: HTTP Cookies
        Returns:
            coroutine : result of the `_send_request` method. It need to be awaited in order to get the HTTP response
        """
        request = Request(Methods.delete.value, self.make_url(url), params=params, headers=headers, cookies=cookies)
        return await self._send_request(request)

    def __call__(self, *args, **kwargs):
        """
        Will trow an error that avoid BaseRESTAsyncClient to be called directly and force use the get_instance class method
        """
        raise TypeError("BaseClient cannot be called directly use get_instance class method instead")


async_client_factory = BaseRESTAsyncClient.get_instance
