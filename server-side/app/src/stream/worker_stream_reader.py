import asyncio
import multiprocessing
import sys
import time
import traceback
from multiprocessing import Process, current_process
from typing import List, Dict

import cv2
from fastapi import WebSocket


class WorkerStreamReader:
    def __init__(self,
                 shared_sources_dict: Dict[int, str],
                 on_done: callable) -> None:
        self.__sources = shared_sources_dict
        self.__sources_lock = multiprocessing.Lock()
        self.__caps: Dict[int, cv2.VideoCapture] = {}
        self.__on_done = on_done

    def add_source(self, source_id, source_str) -> None:
        with self.__sources_lock:
            self.__sources[source_id] = source_str

    def start(self):
        Process(target=self._do_work, name='PROCESS_worker_stream_reader').start()

    def _do_work(self) -> None:
        asyncio.run(self.__do_work())

    async def __do_work(self) -> None:
        while 1:
            try:
                if not self.__handle_source_changes(): continue
                finished_ids = self.__read_caps()
                self.__handle_finished_caps(finished_ids=finished_ids)
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{current_process().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    def __read_caps(self) -> List[int]:
        finished_ids = []
        for (source_id, cap) in self.__caps.items():
            t = time.time()
            success, frame = cap.read()
            print(f'read took {time.time() - t}s')
            enc_frame = None
            if success:
                # processed_frame = self.__simulate_ml_inference(frame)
                t = time.time()
                _, enc_frame = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 20])
                print(f'encoded frame took {time.time() - t}')
            else:
                finished_ids.append(source_id)
            self.__on_done((source_id, enc_frame, success))
        return finished_ids

    def __handle_finished_caps(self, finished_ids: List[int]) -> None:
        with self.__sources_lock:
            for source_id in finished_ids:
                self.__caps[source_id].release()
                del self.__caps[source_id]
                del self.__sources[source_id]

    def __handle_source_changes(self) -> bool:
        with self.__sources_lock:
            if not len(self.__sources):
                return False
            # Handle new sources
            live_source_ids = self.__caps.keys()
            for source_id, source_str in self.__sources.items():
                if source_id not in live_source_ids:
                    video_cap = cv2.VideoCapture(source_str)
                    self.__caps[source_id] = video_cap

            # Handle removed sources (stop streaming)
            expected_source_ids = self.__sources.keys()
            for source_id in self.__caps.keys():
                if source_id not in expected_source_ids:
                    self.__caps[source_id].release()
                    del self.__caps[source_id]

        return True


