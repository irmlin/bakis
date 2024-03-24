import asyncio
from abc import ABC, abstractmethod
from typing import Set

from fastapi import WebSocket


class BaseStreamer(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.connections_lock = asyncio.Lock()
        self.connections: Set[WebSocket] = set()

    async def add_connection(self, websocket: WebSocket):
        async with self.connections_lock:
            self.connections.add(websocket)

    async def remove_connection(self, websocket: WebSocket):
        async with self.connections_lock:
            self.connections.discard(websocket)

    @abstractmethod
    async def stream(self, file_path: str):
        pass


