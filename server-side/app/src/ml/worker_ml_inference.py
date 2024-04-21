import asyncio
import multiprocessing
import queue
import sys
import time
import traceback
from multiprocessing import Process, current_process
from typing import List

import cv2

from ..ml import PickableInferenceSession


class WorkerMLInference:
    def __init__(self, on_done: callable) -> None:
        self.__queue = multiprocessing.Queue(maxsize=500)
        self.__session = PickableInferenceSession(model_path='/home/irmantas/Desktop/bakis/data_prep/output/transformer/video_classifier_every_2nd.onnx')
        self.__on_done = on_done
        self.__parsed = 0

    def add(self, data) -> None:
        try:
            self.__queue.put(data, block=False)
        except queue.Full:
            print(f'WorkerMLInference queue is full! Element not added.')
            return

    def start(self) -> None:
        Process(target=self.__do_work, name='PROCESS_worker_ml_inference').start()

    def __do_work(self) -> None:
        while 1:
            try:
                source_id, batched_frames, success = self.__queue.get(timeout=1)
                self.__parsed += 1
                print(f'INFERENCE. Received data {len(batched_frames)}. Total dequeued: {self.__parsed}.')

                total_frames = len(batched_frames)
                s_time = time.time()
                for i, frame in enumerate(batched_frames):
                    _, enc_frame = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 20])
                    stream_continues = success or (not success and (i < total_frames - 1))
                    # print(f'INFERENCE. Sending source {source_id}, {enc_frame.shape}, {stream_continues}')
                    self.__on_done((source_id, enc_frame, stream_continues))
                print(f'INFERENCE. Done in {time.time() - s_time} seconds.')
            except queue.Empty:
                print('INFERENCE. queue was empty.')
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{current_process().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')
