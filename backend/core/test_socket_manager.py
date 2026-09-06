from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException

from backend.core.socket_manager import FastApiJson, SocketManagerSingleton


def test_fastapi_json_dumps_and_loads():
    data = {"key": "value", "num": 123}
    serialized = FastApiJson.dumps(data)
    assert '"key": "value"' in serialized
    deserialized = FastApiJson.loads(serialized)
    assert deserialized == data


def test_get_cookies_from_environ_http_cookie():
    environ = {"HTTP_COOKIE": "session=abc123xyz; token=test_token"}
    cookies = SocketManagerSingleton._get_cookies_from_environ(environ)
    assert cookies == {"session": "abc123xyz", "token": "test_token"}


def test_get_cookies_from_environ_headers():
    environ = {
        "headers": [
            (b"host", b"localhost"),
            (b"cookie", b"session=header_val%20123"),
        ]
    }
    cookies = SocketManagerSingleton._get_cookies_from_environ(environ)
    assert cookies == {"session": "header_val 123"}


def test_get_cookies_from_environ_empty():
    environ = {}
    cookies = SocketManagerSingleton._get_cookies_from_environ(environ)
    assert cookies == {}


def test_socket_manager_init_socket():
    app = FastAPI()
    sm = SocketManagerSingleton()

    sm.init_socket(app)

    assert sm.sio is not None
    assert app.state.sio is sm.sio

    # Verify route mounted at /
    mounted_routes = [
        route for route in app.routes if getattr(route, "path", None) == ""
    ]
    assert len(mounted_routes) > 0


@pytest.mark.asyncio
async def test_handle_connect_success():
    app = FastAPI()
    sm = SocketManagerSingleton()
    sm.init_socket(app)

    # Find the registered connect handler
    connect_handler = sm.sio.handlers["/"]["connect"]

    environ = {"HTTP_COOKIE": "session=valid"}
    with patch(
        "backend.core.socket_manager.is_authorized_cookies", new_callable=AsyncMock
    ) as mock_auth:
        mock_auth.return_value = True
        result = await connect_handler("test_sid", environ)
        assert result is True
        mock_auth.assert_awaited_once_with({"session": "valid"})


@pytest.mark.asyncio
async def test_handle_connect_unauthorized():
    app = FastAPI()
    sm = SocketManagerSingleton()
    sm.init_socket(app)

    connect_handler = sm.sio.handlers["/"]["connect"]

    environ = {"HTTP_COOKIE": "session=invalid"}
    with patch(
        "backend.core.socket_manager.is_authorized_cookies", new_callable=AsyncMock
    ) as mock_auth:
        mock_auth.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        result = await connect_handler("test_sid", environ)
        assert result is False


@pytest.mark.asyncio
async def test_emit():
    sm = SocketManagerSingleton()
    mock_sio = MagicMock()
    mock_sio.emit = AsyncMock()
    sm._sio = mock_sio

    await sm.emit("test_event", {"hello": "world"}, room="room1", namespace="/")

    mock_sio.emit.assert_awaited_once_with(
        "test_event",
        {"hello": "world"},
        room="room1",
        namespace="/",
    )
