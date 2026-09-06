import os
from unittest.mock import patch

import pytest

from agent.config import Config


@pytest.fixture(autouse=True)
def reset_config_loaded():
    # Store original state
    orig_loaded = Config._loaded
    Config._loaded = False

    yield

    # Restore original state
    Config._loaded = orig_loaded


@patch.dict(os.environ, {}, clear=True)
@patch("agent.config.load_dotenv")
@patch("agent.config.apply_file_env")
def test_config_empty_env(mock_apply, mock_load):
    Config.load()

    assert Config.HOSTNAME == ""
    assert Config.LOG_LEVEL == "INFO"
    assert Config.AGENT_SECRET is None
    assert Config.ALLOW_UNAUTHENTICATED_AGENT is False
    assert Config.ALLOW_EXEC is False
    assert Config.AGENT_SIGNATURE_TTL == 5
    assert Config.DOCKER_TIMEOUT == 15


@patch.dict(
    os.environ,
    {
        "HOSTNAME": "agent-host",
        "LOG_LEVEL": "debug",
        "AGENT_SECRET": "my-secret",
        "ALLOW_UNAUTHENTICATED_AGENT": "true",
        "ALLOW_EXEC": "true",
        "AGENT_SIGNATURE_TTL": "10",
        "DOCKER_TIMEOUT": "30",
    },
    clear=True,
)
@patch("agent.config.load_dotenv")
@patch("agent.config.apply_file_env")
def test_config_filled_env(mock_apply, mock_load):
    Config.load()

    assert Config.HOSTNAME == "agent-host"
    assert Config.LOG_LEVEL == "DEBUG"
    assert Config.AGENT_SECRET == "my-secret"
    assert Config.ALLOW_UNAUTHENTICATED_AGENT is True
    assert Config.ALLOW_EXEC is True
    assert Config.AGENT_SIGNATURE_TTL == 10
    assert Config.DOCKER_TIMEOUT == 30
