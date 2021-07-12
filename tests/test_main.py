from typing import Type

import pytest
from app.main import BaseRESTAsyncClient, EndPoint


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
    rest_client = http_client(host=host, port=port, protocol=protocol)
    assert rest_client.make_url(rel_url) == expected_full_url


@pytest.mark.http_async
def test_cannot_instantiate_http_client_if_no_host(http_client: Type[BaseRESTAsyncClient]):
    with pytest.raises(ValueError, match="EndPointRegistry error trying to add new client : host is missing"):
        rest_client = http_client(host=None, port=None, protocol=None)


@pytest.mark.http_async
@pytest.mark.parametrize("host, host2", [
    ("first_domain.com", "second_domain.com"),
], ids=["Singleton that can change domain on call"])
def test_http_client_singleton(http_client: Type[BaseRESTAsyncClient], host: str, host2: str):
    rest_client1 = http_client(host=host)
    rest_client2 = http_client(host=host2)
    assert hex(id(rest_client1)) == hex(id(rest_client2))


@pytest.mark.http_async
@pytest.mark.parametrize("host, port, protocol, expected_url", [
    ("first_domain.com", 8080, "https", "https://first_domain.com:8080"),
], ids=["Url is build with domain, port and protocol"])
def test_end_point_data_class(host: str, port: int, protocol: str,
                              expected_url: str):
    endpoint = EndPoint(host, port, protocol)

    assert endpoint.base_url == expected_url
