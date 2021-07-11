import httpx
import re
from nanoid import generate
from .singleton import SingletonMeta


class BaseRESTAsyncClient(metaclass=SingletonMeta):
    DEFAULT_PROTOCOL = "http"

    def __init__(self, host, port=None, protocol=DEFAULT_PROTOCOL):
        self.host = host
        self.port = port
        self.protocol = protocol if protocol else self.DEFAULT_PROTOCOL
        self._request_id = None

    @classmethod
    def set_request_id(cls):
        """
        Setter for the request id
        TODO: Check if there is any pre existing request ID from the incoming request headers and generate one ONLY IF there is no
        :return: Nano ID
        """
        cls.instance.request_id = generate()
        return cls.instance.request_id

    @property
    def request_id(self):
        """
        Getter for the request id
        :return:
        """
        if not self._request_id:
            return None
        return str(self._request_id)

    def make_url(self, url: str = ""):
        """
        Url builder based on the host base url
        :param url: relative url that will be concatenate wil the host base url
        :return: An absolute url including the protocol, the host base url, port (if any) and the relative url if any
        """
        if not self.host:
            raise ValueError("make url was called on a not valid client : host is missing")
        # Ensure to remove keep only one "/" along all the url
        url = re.sub('/+', '/', url)
        # remove the first "/" at the beginning
        url = re.sub('^/', '', url)

        return f"{self.protocol}://{self.host}:{self.port}/{url}" if self.port \
            else f"{self.protocol}://{self.host}/{url}"


