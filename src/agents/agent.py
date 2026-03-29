"""
Minimal p9i Agent: WSSClient + ShellService
Без FileWatcher
"""

import asyncio
import json
import subprocess
import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# === Enums ===

# === Constants ===

SHELL_TIMEOUT = 30.0  # seconds
MAX_RETRIES = 5
RECONNECT_BASE_DELAY = 1.0  # seconds, exponential backoff


# === Enums ===

class MessageType(str, Enum):
    """Типы сообщений 9P"""
    TVERSION = "tversion"
    RVERSION = "rversion"
    TWALK = "twalk"
    RWALK = "rwalk"
    TOPEN = "topen"
    ROPEN = "ropen"
    TREAD = "tread"
    RREAD = "rread"
    TWRITE = "twrite"
    RWRITE = "rwrite"
    TCLUNK = "tclunk"
    RCLUNK = "rclunk"
    # p9i extensions
    SHELL_EXEC = "shell.exec"
    SHELL_RESULT = "shell.result"


# === Data Classes ===

@dataclass
class Message:
    """Сообщение 9P/p9i"""
    type: MessageType
    tag: int = 0
    data: Any = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "tag": self.tag,
            "data": self.data,
        })

    @classmethod
    def from_json(cls, raw: str) -> "Message":
        obj = json.loads(raw)
        return cls(
            type=MessageType(obj["type"]),
            tag=obj.get("tag", 0),
            data=obj.get("data"),
        )


@dataclass
class ShellResult:
    """Результат выполнения shell команды"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    error: Optional[str] = None


# === WSSClient ===

class WSSClient:
    """
    WebSocket клиент для p9i Agent.
    Управляет соединением и обменом сообщений с сервером.
    """

    def __init__(
        self,
        url: str,
        on_connect: Optional[Callable[[], Awaitable[None]]] = None,
        on_disconnect: Optional[Callable[[], Awaitable[None]]] = None,
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
    ):
        self.url = url
        self._ws: Optional[Any] = None
        self._running = False
        self._lock = asyncio.Lock()

        # Callbacks
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_error = on_error

        # Message handlers: type -> callback(data) -> Awaitable
        self._handlers: dict[MessageType, Callable[[Any], Awaitable[None]]] = {}

        # Pending requests for RPC-style calls
        self._pending: dict[str, asyncio.Future] = {}

    def handler(self, msg_type: MessageType):
        """Декоратор для регистрации обработчика сообщений"""

        def decorator(func: Callable[[Any], Awaitable[None]]):
            self._handlers[msg_type] = func
            return func

        return decorator

    async def connect(self, retry: bool = True) -> None:
        """Установить WebSocket соединение с reconnect"""
        import websockets

        async def _do_connect() -> None:
            self._ws = await websockets.connect(
                self.url,
                ping_interval=30,
                ping_timeout=10,
            )
            self._running = True
            logger.info(f"WSS: Connected to {self.url}")

        # Try with exponential backoff
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES if retry else 1):
            try:
                await _do_connect()
                if self.on_connect:
                    await self.on_connect()
                return
            except Exception as e:
                last_error = e
                if retry and attempt < MAX_RETRIES - 1:
                    delay = RECONNECT_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"WSS: Connect failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"WSS: Connection failed after {MAX_RETRIES} attempts: {e}")
                    if self.on_error:
                        await self.on_error(e)
                    raise

    async def disconnect(self) -> None:
        """Закрыть соединение"""
        self._running = False

        if self._ws:
            await self._ws.close()
            self._ws = None

        # Cancel pending requests
        for fut in self._pending.values():
            if not fut.done():
                fut.cancel()
        self._pending.clear()

        logger.info("WSS: Disconnected")

        if self.on_disconnect:
            await self.on_disconnect()

    async def send(self, message: Message) -> None:
        """Отправить сообщение"""
        if not self._ws or not self._running:
            raise ConnectionError("Not connected")

        raw = message.to_json()
        await self._ws.send(raw)
        logger.debug(f"WSS: Sent -> {message.type.value}")

    async def request(
        self,
        msg_type: MessageType,
        data: Any = None,
        timeout: float = 30.0,
    ) -> Any:
        """
        Отправить запрос и дождаться ответа (RPC-style).
        Возвращает data из ответа.
        """
        import websockets

        msg_id = str(uuid.uuid4())
        msg = Message(type=msg_type, tag=0, data=data)

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future

        try:
            await self.send(msg)
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request {msg_type.value} timed out after {timeout}s")
        finally:
            self._pending.pop(msg_id, None)

    async def receive_loop(self, auto_reconnect: bool = True) -> None:
        """Основной цикл приёма сообщений с auto-reconnect"""
        import websockets

        while self._running:
            try:
                if not self._ws:
                    # Retry connection
                    for attempt in range(MAX_RETRIES):
                        try:
                            await self.connect(retry=False)
                            break
                        except Exception as e:
                            if attempt < MAX_RETRIES - 1:
                                delay = RECONNECT_BASE_DELAY * (2 ** attempt)
                                logger.warning(f"WSS: Reconnect failed, retrying in {delay}s...")
                                await asyncio.sleep(delay)
                            else:
                                raise

                if not self._ws:
                    break

                raw = await self._ws.recv()
                msg = Message.from_json(raw)
                logger.debug(f"WSS: Received <- {msg.type.value}")

                await self._dispatch(msg)

            except websockets.exceptions.ConnectionClosed:
                logger.warning("WSS: Connection closed, attempting reconnect...")
                self._ws = None
                if not auto_reconnect:
                    break
            except Exception as e:
                logger.error(f"WSS: Receive error: {e}")
                self._ws = None
                if not auto_reconnect:
                    if self.on_error:
                        await self.on_error(e)
                    break
                # Will retry connection on next iteration

        if self._ws:
            await self.disconnect()

    async def _dispatch(self, msg: Message) -> None:
        """Диспетчеризация сообщения обработчикам"""
        # Check if it's a response to a pending request
        for future in self._pending.values():
            if not future.done():
                future.set_result(msg.data)
                return

        # Otherwise call registered handler
        handler = self._handlers.get(msg.type)
        if handler:
            try:
                await handler(msg.data)
            except Exception as e:
                logger.error(f"Handler error for {msg.type.value}: {e}")


# === ShellService ===

class ShellService:
    """
    Сервис выполнения shell команд.
    Интегрируется с WSSClient для удалённого выполнения.
    """

    def __init__(
        self,
        client: WSSClient,
        working_dir: str = ".",
        env: Optional[dict[str, str]] = None,
    ):
        self.client = client
        self.working_dir = working_dir
        self.env = env or {}
        self._active_procs: dict[str, asyncio.subprocess.Process] = {}

        # Register message handlers
        client._handlers[MessageType.SHELL_EXEC] = self._handle_exec

    async def _handle_exec(self, data: dict) -> None:
        """Обработать запрос на выполнение команды"""
        cmd_id = data.get("id", str(uuid.uuid4()))
        command = data.get("command", "")
        cwd = data.get("cwd", self.working_dir)
        input_data = data.get("input", "")

        logger.info(f"Shell: Executing [{cmd_id}] {command}")

        try:
            result = await self._execute(command, cwd, input_data)
            response_type = MessageType.SHELL_RESULT
            response_data = {
                "id": cmd_id,
                **result,
            }
        except Exception as e:
            logger.error(f"Shell: Execution error [{cmd_id}]: {e}")
            response_data = {
                "id": cmd_id,
                "success": False,
                "error": str(e),
                "returncode": -1,
            }

        await self.client.send(Message(
            type=MessageType.SHELL_RESULT,
            data=response_data,
        ))

    async def _execute(
        self,
        command: str,
        cwd: str,
        input_data: str,
    ) -> dict:
        """Выполнить команду и вернуть результат с timeout"""
        # Build environment
        env = {**self.env, **self._get_remote_env()}

        # Execute via shell
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=env,
        )

        self._active_procs[command] = proc

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(input=input_data.encode() if input_data else None),
                timeout=SHELL_TIMEOUT,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            self._active_procs.pop(command, None)
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {SHELL_TIMEOUT}s",
                "returncode": -1,
            }

        self._active_procs.pop(command, None)

        return {
            "success": proc.returncode == 0,
            "stdout": stdout_bytes.decode("utf-8", errors="replace"),
            "stderr": stderr_bytes.decode("utf-8", errors="replace"),
            "returncode": proc.returncode,
        }

    def _get_remote_env(self) -> dict:
        """Получить переменные окружения от удалённого клиента"""
        return {
            "P9I_AGENT": "1",
        }

    async def exec_local(
        self,
        command: str,
        cwd: Optional[str] = None,
    ) -> ShellResult:
        """
        Локальное выполнение команды (без отправки на сервер).
        Полезно для служебных операций агента.
        """
        result = await self._execute(
            command,
            cwd or self.working_dir,
            "",
        )
        return ShellResult(
            success=result["success"],
            stdout=result["stdout"],
            stderr=result["stderr"],
            returncode=result["returncode"],
        )


# === p9i Agent ===

class Agent:
    """
    Minimal p9i Agent.
    Объединяет WSSClient и ShellService.
    """

    VERSION = "0.1.0"
    PROTOCOL = "9P2000"

    def __init__(
        self,
        server_url: str,
        working_dir: str = ".",
        agent_id: Optional[str] = None,
    ):
        self.agent_id = agent_id or f"agent-{uuid.uuid4().hex[:8]}"
        self.working_dir = working_dir

        # Initialize client
        self.client = WSSClient(
            url=server_url,
            on_connect=self._on_connect,
            on_disconnect=self._on_disconnect,
        )

        # Initialize shell service
        self.shell = ShellService(
            client=self.client,
            working_dir=working_dir,
        )

        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def _on_connect(self) -> None:
        """Callback при подключении"""
        logger.info(f"Agent [{self.agent_id}] connected")

        # Announce presence
        await self.client.send(Message(
            type=MessageType.TVERSION,
            data={
                "agent_id": self.agent_id,
                "version": self.VERSION,
                "protocol": self.PROTOCOL,
                "features": ["shell"],
            },
        ))

    async def _on_disconnect(self) -> None:
        """Callback при отключении"""
        logger.info(f"Agent [{self.agent_id}] disconnected")

    async def start(self) -> None:
        """Запустить агента"""
        if self._running:
            return

        self._running = True
        logger.info(f"Agent [{self.agent_id}] starting...")

        try:
            await self.client.connect()

            # Run receive loop
            receive_task = asyncio.create_task(
                self.client.receive_loop(),
                name="wss-receive",
            )
            self._tasks.append(receive_task)

            # Wait for tasks
            await asyncio.gather(*self._tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"Agent error: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Остановить агента"""
        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        await self.client.disconnect()

        logger.info(f"Agent [{self.agent_id}] stopped")


# === Mock Server for Testing ===

class MockServer:
    """Mock WebSocket сервер для тестирования"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self._server = None
        self._clients: set[Any] = set()
        self._running = False

    async def start(self) -> None:
        import websockets

        self._running = True

        async def handler(ws, path):
            self._clients.add(ws)
            logger.info(f"Server: Client connected ({len(self._clients)})")

            try:
                async for raw in ws:
                    msg = json.loads(raw)
                    msg_type = msg.get("type")
                    data = msg.get("data", {})

                    logger.info(f"Server: Received {msg_type}")

                    if msg_type == "shell.exec":
                        # Echo back as result (simplified)
                        await ws.send(json.dumps({
                            "type": "shell.result",
                            "data": {
                                "id": data.get("id"),
                                "success": True,
                                "stdout": f"Echo: {data.get('command', '')}",
                                "stderr": "",
                                "returncode": 0,
                            },
                        }))
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self._clients.discard(ws)
                logger.info(f"Server: Client disconnected ({len(self._clients)})")

        self._server = await websockets.serve(handler, self.host, self.port)
        logger.info(f"Mock server started on ws://{self.host}:{self.port}")

    async def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("Mock server stopped")


if __name__ == "__main__":
    import sys

    async def main():
        """Main entry point for testing"""
        server = MockServer()
        await server.start()
        print("Mock server running on ws://localhost:8765")
        print("Press Ctrl+C to stop")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await server.stop()

    asyncio.run(main())