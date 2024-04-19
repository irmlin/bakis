import asyncio
import random
import time
from typing import List, Tuple, Dict
from multiprocessing import Process, Manager
import multiprocessing

import cv2
from fastapi import WebSocket

from .worker_base import WorkerBase


class WorkerStreamReader:
    def __init__(self,
                 shared_sources_dict: Dict[int, str],
                 shared_connections_dict: Dict[int, List[WebSocket]],
                 on_done: callable) -> None:
        self.__sources = shared_sources_dict
        self.__connections = shared_connections_dict
        self.__sources_lock = multiprocessing.Lock()
        self.__connections_lock = multiprocessing.Lock()
        self.__caps: Dict[int, cv2.VideoCapture] = {}
        self.__on_done = on_done

    def add_source(self, source_id, source_str) -> None:
        with self.__sources_lock:
            print('inside soruces lock')
            self.__sources[source_id] = source_str
        with self.__connections_lock:
            print('inside connections lock')
            self.__connections[source_id] = []

    async def subscribe_connection(self, source_id: int, websocket: WebSocket) -> None:
        # live_source_ids = self.__caps.keys()
        # if source_id not in live_source_ids:
        #     # Stream not running
        #     return

        await websocket.accept()
        print('websocket')
        print(websocket)
        with self.__connections_lock:
            print(f'before adding connection: {self.__connections}')
            print('websocket')
            print(websocket)
            self.__connections[source_id].append(websocket)
            print(f'after adding connection: {self.__connections}')

    async def unsubscribe_connection(self, source_id: int, websocket: WebSocket):
        # live_source_ids = self.__caps.keys()
        # if source_id not in live_source_ids:
        #     # Stream not running
        #     return
        with self.__connections_lock:
            self.__connections[source_id].remove(websocket)

    def start(self):
        Process(target=self._do_work).start()

    def _do_work(self) -> None:
        asyncio.run(self.__do_work())

    async def __do_work(self) -> None:
        while 1:
            try:
                with self.__sources_lock:
                    if not len(self.__sources):
                        continue
                    self.__handle_source_changes()
                    finished_caps = []
                    for i, (source_id, cap) in enumerate(self.__caps.items()):
                        t = time.time()
                        ret, frame = cap.read()
                        print(f'read took {time.time() - t}')
                        if not ret:
                            finished_caps.append(i)
                            continue

                        # processed_frame = self.__simulate_ml_inference(frame)
                        t = time.time()
                        _, enc_frame = cv2.imencode(".jpg", frame)
                        print(f'encode took {time.time() - t}')
                        self.__on_done((source_id, enc_frame))
                        # with self.__connections_lock:
                        #     print('inside lock')
                        #     print(self.__connections.keys(), source_id, 'conenctions:', len(self.__connections[source_id]))
                        #     for ws in self.__connections[source_id]:
                        #         await ws.send_bytes(enc_frame.tobytes())
                        #     await asyncio.sleep(1)
                    #     print('trinu video')
                    #     self.__video_caps[i].release()
                    #     del self.__video_caps[i]

            except BaseException as e:
                print('some error')

    def __handle_source_changes(self) -> None:
        # Lock acquired outside of method, save to use shared __sources list

        # Handle new sources
        live_source_ids = self.__caps.keys()
        for source_id, source_str in self.__sources.items():
            if source_id not in live_source_ids:
                video_cap = cv2.VideoCapture(source_str)
                self.__caps[source_id] = video_cap
                print(f'ADDED NEW CAP, {len(self.__sources)}, {len(self.__caps)}')

        # Handle removed sources (stop streaming)
        expected_source_ids = self.__sources.keys()
        for source_id in self.__caps.keys():
            if source_id not in expected_source_ids:
                self.__caps[source_id].release()
                del self.__caps[source_id]


