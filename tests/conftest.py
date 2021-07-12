import urllib.request
import pytest
from app.main import BaseRESTAsyncClient

REAL_API_CALL_HOSTS = ["google.com"]

@pytest.fixture
def http_client():
    return BaseRESTAsyncClient.get_instance


@pytest.fixture
def internet_connection():
    try:
        urllib.request.urlopen('https://google.com')
        return True
    except:
        return False


@pytest.fixture
def non_mocked_hosts() -> list:
    return REAL_API_CALL_HOSTS
