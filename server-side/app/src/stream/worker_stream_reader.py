import asyncio
import multiprocessing
import os
import sys
import time
import traceback
from multiprocessing import Process, current_process
from typing import List, Dict, Any

import cv2


class WorkerStreamReader:
    def __init__(self,
                 shared_sources_dict: Dict[int, str],
                 on_done: callable) -> None:
        self.sources = shared_sources_dict
        self.sources_lock = multiprocessing.Lock()
        self.caps: Dict[int, Dict[str, Any]] = {}
        self.on_done = on_done
        self.process = None

    def add_source(self, source_id, source_str) -> None:
        print('trying')
        with self.sources_lock:
            self.sources[source_id] = source_str
        print('done')

    def remove_source(self, source_id):
        with self.sources_lock:
            if source_id in self.sources.keys():
                del self.sources[source_id]

    def start(self):
        self.process = Process(target=self.__do_work, name='PROCESS_worker_stream_reader')
        self.process.start()

    def stop(self) -> None:
        if self.process is not None:
            if self.process.is_alive():
                self.process.terminate()
                self.process.join()
            self.process = None

    def __do_work(self) -> None:
        while 1:
            try:
                removed_sources = self.__handle_source_changes()
                self.__inform_about_removed_sources(removed_sources=removed_sources)
                finished_ids = self.__read_caps()
                self.__handle_finished_caps(finished_ids=finished_ids)
                self.__rest()
            except BaseException as e:
                time.sleep(5)
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{current_process().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    def __rest(self):
        if len(self.caps) == 0:
            time.sleep(1)

    def __read_caps(self) -> List[int]:
        finished_ids = []
        for (source_id, cap_info) in self.caps.items():
            if not self.__should_read_cap(source_id): continue
            self.__update_fps_info(source_id)
            success, frame = cap_info['cap'].read()
            if success:
                self.caps[source_id]['num_read'] += 1
            else:
                finished_ids.append(source_id)

            self.on_done((source_id, frame, success))

        return finished_ids

    def __inform_about_removed_sources(self, removed_sources: List[int]) -> None:
        for source_id in removed_sources:
            self.on_done((source_id, None, False))


    def __update_fps_info(self, source_id):
        if self.caps[source_id]['num_read'] >= self.caps[source_id]['fps']:
            self.caps[source_id]['num_read'] = 0
            self.caps[source_id]['start_time'] = time.time()

    def __should_read_cap(self, source_id) -> bool:
        num_read = self.caps[source_id]['num_read']
        fps = self.caps[source_id]['fps']
        start_time = self.caps[source_id]['start_time']
        return (
            num_read < fps or
            time.time() - start_time >= 1.0
        )

    def __handle_finished_caps(self, finished_ids: List[int]) -> None:
        with self.sources_lock:
            for source_id in finished_ids:
                self.caps[source_id]['cap'].release()
                del self.caps[source_id]
                del self.sources[source_id]

    def __handle_source_changes(self) -> List[int]:
        removed_sources = []
        with self.sources_lock:
            # Handle new sources
            live_source_ids = self.caps.keys()
            for source_id, source_str in self.sources.items():
                if source_id not in live_source_ids:
                    print(source_str)
                    video_cap = cv2.VideoCapture(source_str)
                    self.caps[source_id] = {
                        'cap': video_cap,
                        'fps': video_cap.get(cv2.CAP_PROP_FPS),
                        'start_time': time.time(),
                        'num_read': 0
                    }
                    print(f'READER, added {source_id}, FPS: {self.caps[source_id]["fps"]}')

            # Handle removed sources (stop streaming)
            expected_source_ids = self.sources.keys()
            for source_id in list(self.caps.keys()):
                if source_id not in expected_source_ids:
                    print(f'READER, removed {source_id}')
                    removed_sources.append(source_id)
                    self.caps[source_id]['cap'].release()
                    del self.caps[source_id]

        return removed_sources
