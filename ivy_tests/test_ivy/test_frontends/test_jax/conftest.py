import pytest
from ...conftest import mod_frontend
import sys, os
sys.path.append((os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))


@pytest.fixture(scope="session")
def frontend():
    if mod_frontend["jax"]:
        return mod_frontend["jax"]
    return "jax"
