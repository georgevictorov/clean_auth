import time

import pytest
import requests

from tests.e2e.cli.test_cli import enter_password_pair, finish_cli, run_cli

BASE_URL = "http://api"
NUM_RETRIES = 5


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    for _ in range(NUM_RETRIES):
        try:
            response = requests.get(f"{BASE_URL}/ping")
            assert response.status_code == 200
            assert response.json() == {"msg": "pong"}

            return
        except requests.ConnectionError:
            time.sleep(1)

    pytest.fail("api did not respond")


@pytest.fixture
def client():
    with requests.Session() as session:
        yield session


@pytest.fixture
def api_url():
    return BASE_URL


@pytest.fixture
def user():
    username = "john"
    password = "password123"

    child = run_cli("create-user", username)

    try:
        enter_password_pair(child, password)
        exitstatus, output = finish_cli(child)
    finally:
        if child.isalive():
            child.close(force=True)

    assert exitstatus == 0, output

    return {
        "username": username,
        "password": password,
    }
