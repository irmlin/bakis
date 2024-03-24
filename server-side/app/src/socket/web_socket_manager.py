import asyncio
from typing import Dict, Set

from fastapi import WebSocket

from ..stream import MLStreamer, BaseStreamer


class WebSocketManager:

    def __init__(self):
        self.streamers: Dict[int, BaseStreamer] = {}

    async def add_stream(self, video_id, file_path):
        if video_id in self.streamers:
            # Stream already running
            return

        streamer = MLStreamer()
        self.streamers[video_id] = streamer
        # await asyncio.create_task(streamer.stream(file_path))
        await streamer.stream(file_path)

    async def subscribe(self, video_id: int, websocket: WebSocket) -> None:
        if video_id not in self.streamers:
            # Stream not running
            return

        await websocket.accept()
        streamer = self.streamers[video_id]
        await streamer.add_connection(websocket)

    async def unsubscribe(self, video_id: int, websocket: WebSocket):
        if video_id not in self.streamers:
            # Stream not running
            return
        streamer = self.streamers[video_id]
        await streamer.remove_connection(websocket)
