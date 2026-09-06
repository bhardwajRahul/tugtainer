import json
import logging
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import unquote

import socketio
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder

from backend.modules.auth.auth_util import is_authorized_cookies

logger = logging.getLogger("socket_manager")


class FastApiJson:
    @staticmethod
    def dumps(*args: Any, **kwargs: Any) -> str:
        if args:
            args = (jsonable_encoder(args[0]), *args[1:])
        return json.dumps(*args, **kwargs)

    @staticmethod
    def loads(*args: Any, **kwargs: Any) -> Any:
        return json.loads(*args, **kwargs)


class SocketManagerSingleton:
    _instance: "SocketManagerSingleton | None" = None
    _sio: socketio.AsyncServer | None = None

    def __new__(cls) -> "SocketManagerSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def sio(self) -> socketio.AsyncServer | None:
        return self._sio

    @staticmethod
    def _get_cookies_from_environ(environ: dict[str, Any]) -> dict[str, str]:
        cookie_str = environ.get("HTTP_COOKIE", "")
        if not cookie_str:
            headers = environ.get("headers", [])
            for k, v in headers:
                if k == b"cookie":
                    cookie_str = v.decode("utf-8")
                    break

        cookies = SimpleCookie()
        cookies.load(cookie_str)
        return {k: unquote(m.value) for k, m in cookies.items()}

    def init_socket(self, app: FastAPI) -> None:
        sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            cors_credentials=True,
            json=FastApiJson,
        )
        self._sio = sio
        sio_app = socketio.ASGIApp(
            socketio_server=sio,
            socketio_path="ws/socket.io",
        )
        app.mount("/", sio_app)

        app.state.sio = sio

        async def handle_connect(
            sid: str, environ: dict[str, Any], auth: Any = None
        ) -> bool:
            logger.debug(f"Socket connection attempt sid={sid}")
            try:
                cookies = self._get_cookies_from_environ(environ)
                await is_authorized_cookies(cookies)
                return True
            except HTTPException as e:
                logger.warning(f"Socket connection rejected sid={sid}: {e.detail}")
                return False

        async def handle_disconnect(sid: str) -> None:
            logger.debug(f"Socket disconnected sid={sid}")

        sio.on("connect", handle_connect)
        sio.on("disconnect", handle_disconnect)

    async def emit(
        self, event: str, data: Any, room: str | None = None, namespace: str = "/"
    ) -> None:
        if self._sio is not None:
            await self._sio.emit(
                event, jsonable_encoder(data), room=room, namespace=namespace
            )


socket_manager = SocketManagerSingleton()
