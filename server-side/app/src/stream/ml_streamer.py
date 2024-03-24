import asyncio
import base64
import random
from typing import Set

import cv2
import numpy as np
from fastapi import WebSocket

from .base_streamer import BaseStreamer


class MLStreamer(BaseStreamer):

    def __init__(self):
        super().__init__()

    async def stream(self, file_path: str):
        video_capture = cv2.VideoCapture(file_path)
        i = 0
        while True:
            i += 1
            ret, frame = video_capture.read()
            if not ret:
                break

            processed_frame = self.__simulate_ml_inference(frame)
            _, enc_frame = cv2.imencode(".jpg", processed_frame)

            async with self.connections_lock:
                for ws in self.connections:
                    # try:
                    #     await ws.send_text(f'Sending {i}!')
                    # except Exception as e:
                    #     print(f"Error sending data to WebSocket: {e}")
                    try:
                        print(i)
                        await ws.send_bytes(enc_frame.tobytes())
                    except Exception as e:
                        print(f"Error sending data to WebSocket: {e}")
            await asyncio.sleep(0)

        # video_capture.release()

    @staticmethod
    def __simulate_ml_inference(frame: np.ndarray):
        cur_shape = frame.shape
        new_shape = (cur_shape[1] * 2, cur_shape[0] * 2)
        half_frame = cv2.resize(frame, dsize=new_shape)
        return cv2.cvtColor(half_frame, cv2.COLOR_RGB2RGBA)