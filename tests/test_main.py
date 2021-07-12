from typing import Type, Any
import pytest
from pytest_httpx import HTTPXMock
from app.main import BaseRESTAsyncClient, EndPoint


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
        "rall redundant slashes are removed from url",
        "work without the first slash"])
def test_make_url(http_client: Type[BaseRESTAsyncClient], host, port, protocol, rel_url, expected_full_url):
    rest_client = http_client(host=host, port=port, protocol=protocol)
    assert rest_client().make_url(rel_url) == expected_full_url


@pytest.mark.http_async
def test_cannot_instantiate_http_client_if_no_host(http_client: Type[BaseRESTAsyncClient]):
    with pytest.raises(ValueError, match="EndPointRegistry error trying to add new client : host is missing"):
        rest_client = http_client(host=None, port=None, protocol=None)
        rest_client()


@pytest.mark.http_async
@pytest.mark.parametrize("host, host2, url1, url2", [
    ("first_domain.com", "second_domain.com", "http://first_domain.com", "http://second_domain.com"),
], ids=["Singleton that can change domain on call"])
def test_http_client_singleton(http_client: Type[BaseRESTAsyncClient], host: str, host2: str, url1: str, url2: str):
    rest_client1 = http_client(host=host)
    rest_client2 = http_client(host=host2)
    # assert that addresses are the same (singleton)
    assert hex(id(rest_client1())) == hex(id(rest_client2()))
    # assert that calling each client base url getter will return the corresponding url from the registry
    assert rest_client1().get_base_url() == url1
    assert rest_client2().get_base_url() == url2


@pytest.mark.http_async
@pytest.mark.parametrize("host, port, protocol, expected_url", [
    ("first_domain.com", 8080, "https", "https://first_domain.com:8080"),
], ids=["Url is build with domain, port and protocol"])
def test_end_point_data_class(host: str, port: int, protocol: str,
                              expected_url: str):
    endpoint = EndPoint(host, port, protocol)
    assert endpoint.base_url == expected_url


@pytest.mark.http_async
@pytest.mark.asyncio
@pytest.mark.parametrize("host, port, protocol, expected_status_code", [
    ("localhost", 3000, "http", 200),
], ids=["Async get return expected status code"])
async def test_get_async(http_client, internet_connection, httpx_mock, monkeypatch, host: str, port: int, protocol: str,
                         expected_status_code: int):
    if not internet_connection:
        host = "local"
        httpx_mock.add_response(status_code=expected_status_code)

    rest_client = http_client(host=host, port=port, protocol=protocol)
    response = await rest_client().get("content")
    assert response.status_code == expected_status_code


@pytest.mark.http_async
@pytest.mark.asyncio
@pytest.mark.parametrize("host, port, protocol, expected_status_code", [
    ("localhost", 3000, "http", 204),
], ids=["Async delete return expected status code"])
async def test_delete_async(http_client, internet_connection, httpx_mock, monkeypatch, host: str, port: int,
                            protocol: str,
                            expected_status_code: int):
    if not internet_connection:
        host = "local"
        httpx_mock.add_response(status_code=expected_status_code)

    rest_client = http_client(host=host, port=port, protocol=protocol)
    response = await rest_client().delete("content")
    assert response.status_code == expected_status_code


@pytest.mark.http_async
@pytest.mark.asyncio
@pytest.mark.parametrize("host, port, protocol, body, headers, expected_status_code", [
    ("localhost", 3000, "http",
     {
         "title": 'foo',
         "body": 'bar',
         "userId": 1,
     },
     {
         'Content-type': 'application/json; charset=UTF-8',
     },
     201),
], ids=["Async post return expected status code"])
async def test_post_async(http_client, internet_connection, httpx_mock, monkeypatch, host: str, port: int,
                          protocol: str, body: dict[str, Any], headers: dict[str, str],
                          expected_status_code: int):
    if not internet_connection:
        host = "local"
        httpx_mock.add_response(status_code=expected_status_code)

    rest_client = http_client(host=host, port=port, protocol=protocol)
    response = await rest_client().post("content", headers=headers, data=body)
    assert response.status_code == expected_status_code


@pytest.mark.http_async
@pytest.mark.asyncio
@pytest.mark.parametrize("host, port, protocol, body, headers, expected_status_code", [
    ("localhost", 3000, "http",
     {
         "title": "",
         "body": "",
         "userId": 1,
     },
     {
         'Content-type': 'application/json; charset=UTF-8',
     },
     204),
], ids=["Async put return expected status code"])
async def test_put_async(http_client, internet_connection, httpx_mock, monkeypatch, host: str, port: int,
                         protocol: str, body: dict[str, Any], headers: dict[str, str],
                         expected_status_code: int):
    if not internet_connection:
        host = "local"
        httpx_mock.add_response(status_code=expected_status_code)

    rest_client = http_client(host=host, port=port, protocol=protocol)
    response = await rest_client().put("content", headers=headers, data=body)
    assert response.status_code == expected_status_code
