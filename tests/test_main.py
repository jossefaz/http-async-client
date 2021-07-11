from typing import Type

import pytest
from app.main import BaseRESTAsyncClient


@pytest.fixture
def http_client() -> Type[BaseRESTAsyncClient]:
    return BaseRESTAsyncClient


@pytest.mark.http_async
@pytest.mark.parametrize("host, port, protocol, rel_url, expected_full_url", [
    ("example.com", None, None, "/gene/diseases/query",
     "http://example.com/gene/diseases/query"),
    ("example.com", 8080, "https", "/gene/diseases/query",
     "https://example.com:8080/gene/diseases/query"),
    ("example.com", None, None, "/////gene///diseases//query",
     "http://example.com/gene/diseases/query"),
    ("example.com", None, None, "gene///diseases//query",
     "http://example.com/gene/diseases/query"),
], ids=["Build a url with no port or protocol",
        "Build a url with a port and protocol",
        "remove all redundant slashes",
        "work without the first slash"])
def test_make_url(http_client: Type[BaseRESTAsyncClient], host, port, protocol, rel_url, expected_full_url):
    rest_client = http_client(host, port, protocol)
    assert rest_client.make_url(rel_url) == expected_full_url


@pytest.mark.http_async
def test_make_url_raise_value_error_if_no_host(http_client: Type[BaseRESTAsyncClient]):
    rest_client = http_client(None, None, None)
    with pytest.raises(ValueError, match="make url was called on a not valid client : host is missing") as exc_info:
        rest_client.make_url("/test")


@pytest.mark.http_async
@pytest.mark.parametrize("host, host2", [
    ("first_domain.com", "second_domain.com"),
], ids=["Singleton that can change domain on call"])
def test_http_client_singleton(http_client: Type[BaseRESTAsyncClient], host: str, host2: str):
    rest_client1 = http_client(host)
    rest_client2 = http_client(host2)
    assert hex(id(rest_client1)) == hex(id(rest_client2))
