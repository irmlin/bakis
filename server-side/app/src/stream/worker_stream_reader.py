import asyncio
import multiprocessing
import sys
import time
import traceback
from multiprocessing import Process, current_process
from typing import List, Dict, Any
from time import time as timer

import cv2
from fastapi import WebSocket


class WorkerStreamReader:
    def __init__(self,
                 shared_sources_dict: Dict[int, str],
                 on_done: callable) -> None:
        self.__sources = shared_sources_dict
        self.__sources_lock = multiprocessing.Lock()
        self.__caps: Dict[int, Dict[str, Any]] = {}
        self.__on_done = on_done
        self.__batch_size = 5
        self.__batch_data = dict()
        self.__enqueued = 0

    def add_source(self, source_id, source_str) -> None:
        with self.__sources_lock:
            self.__sources[source_id] = source_str

    def remove_source(self, source_id):
        with self.__sources_lock:
            if source_id in self.__sources.keys():
                del self.__sources[source_id]

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
        for (source_id, cap_info) in self.__caps.items():
            if not self.__should_read_cap(source_id):
                # print(f"READER. Not reading {source_id} frames. Time passed since last batch sent: {timer() - self.__batch_data[source_id]['start_time']}."
                #       f"Expected time to pass: {self.__batch_size / self.__caps[source_id]['fps']}")
                continue
            self.__clear_batch_if_full(source_id)
            success, frame = cap_info['cap'].read()
            if success:
                self.__batch_data[source_id]['frames'].append(frame)
                # print(
                #     f"READER. Appended frame for {source_id}. Batch full {len(self.__batch_data[source_id]['frames'])}/{self.__batch_size}")
            else:
                finished_ids.append(source_id)
            # Batch is full or stream ended -> send batch downstream
            if self.__batch_full(source_id) or not success:
                self.__enqueued += 1
                print(f"READER. Sending batch of {len(self.__batch_data[source_id]['frames'])} frames. Success was {success}."
                      f"Took {timer() - self.__batch_data[source_id]['start_time']} seconds to read full batch. "
                      f"Total enqueued: {self.__enqueued}")
                self.__on_done((source_id, self.__batch_data[source_id]['frames'][:], success))
        return finished_ids

    def __should_read_cap(self, source_id: int) -> bool:
        return (
            not self.__batch_full(source_id) or
            timer() - self.__batch_data[source_id]['start_time'] > self.__batch_size / self.__caps[source_id]['fps']
            # timer() - self.__batch_data[source_id]['start_time'] > self.__batch_size / 60
        )

    def __clear_batch_if_full(self, source_id) -> None:
        if self.__batch_full(source_id):
            self.__batch_data[source_id]['frames'].clear()
            # Mark time of first frame in batch
            self.__batch_data[source_id]['start_time'] = timer()

    def __batch_full(self, source_id):
        return len(self.__batch_data[source_id]['frames']) >= self.__batch_size

    def __handle_finished_caps(self, finished_ids: List[int]) -> None:
        with self.__sources_lock:
            for source_id in finished_ids:
                self.__caps[source_id]['cap'].release()
                del self.__caps[source_id]
                del self.__sources[source_id]
                del self.__batch_data[source_id]

    def __handle_source_changes(self) -> bool:
        with self.__sources_lock:
            if not len(self.__sources):
                return False

            # Handle new sources
            live_source_ids = self.__caps.keys()
            for source_id, source_str in self.__sources.items():
                if source_id not in live_source_ids:
                    video_cap = cv2.VideoCapture(source_str)
                    self.__caps[source_id] = {
                        'cap': video_cap,
                        'fps': video_cap.get(cv2.CAP_PROP_FPS)
                    }
                    self.__batch_data[source_id] = {
                        'frames': [],
                        'start_time': timer()
                    }

            # Handle removed sources (stop streaming)
            expected_source_ids = self.__sources.keys()
            for source_id in list(self.__caps.keys()):
                if source_id not in expected_source_ids:
                    self.__caps[source_id]['cap'].release()
                    del self.__caps[source_id]
                    del self.__batch_data[source_id]

        return True


