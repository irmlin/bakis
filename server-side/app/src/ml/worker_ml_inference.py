import asyncio
import multiprocessing
import os
import queue
import sys
import time
import traceback
from multiprocessing import Process, current_process
from typing import List, Any, Dict

import cv2
import numpy as np
import onnxruntime as ort

from ..ml import PickableInferenceSession
from ..utilities import execution_time


class WorkerMLInference:
    def __init__(self, on_done: callable, batch_size: int = 30, img_h: int = 128, img_w: int = 128) -> None:
        self.__queue = multiprocessing.Queue(maxsize=500)
        self.__on_done = on_done
        self.__batch_size = batch_size
        self.__img_h = img_h
        self.__img_w = img_w
        self.__batch_data: Dict[int, Dict[str, Any]] = {}
        self.__last_frame_hit = []
        self.__to_delete = []
        self.__feature_extractor_onnx_path = 'app/src/ml/models/feature_extractor_gpu.onnx'
        self.__transformer_onnx_path = 'app/src/ml/models/transformer_gpu.onnx'
        self.__feature_extractor_session = None
        self.__transformer_session = None

    def add(self, data) -> None:
        try:
            self.__queue.put(data, block=True)
        except queue.Full:
            print(f'WorkerMLInference queue is full! Element not added.')
            return

    def start(self) -> None:
        Process(target=self.__do_work, name='PROCESS_worker_ml_inference').start()

    def __do_work(self) -> None:
        self.__feature_extractor_session = (
            ort.InferenceSession(self.__feature_extractor_onnx_path, providers=['CUDAExecutionProvider']))
        self.__transformer_session = (
            ort.InferenceSession(self.__transformer_onnx_path, providers=['CPUExecutionProvider']))
        while 1:
            try:
                # TODO: timeout
                # source_id, frame, success = self.__queue.get(block=True, timeout=0.1)
                source_id, frame, success = self.__queue.get(block=True)
                if source_id not in self.__batch_data.keys():
                    # Initialize new source
                    self.__batch_data[source_id] = {'frames': [], 'ready': False}

                if success:
                    self.__batch_data[source_id]['frames'].append(frame)
                else:
                    self.__last_frame_hit.append(source_id)

                self.__set_batch_ready(source_id, success)

                self.__process_batch()

            except queue.Empty:
                self.__process_batch()
            except BaseException as e:
                time.sleep(5)
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{current_process().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    def __process_batch(self) -> None:
        if not self.__all_batches_ready():
            return

        scores = self.__infer()
        # print(f'ML PREDICTED: {scores}')
        for i in range(self.__batch_size):
            for j, s in enumerate(self.__batch_data.keys()):
                frames = self.__batch_data[s]['frames']
                if len(frames) == 0 and s in self.__last_frame_hit and s not in self.__to_delete:
                    # print(f'ML, SPECIAL. {s}')
                    # Special case, were full batch was sent and then immediately success=False received
                    self.__on_done((s, None, None, None, False))
                    self.__to_delete.append(s)
                if i >= len(frames):
                    # All frames have been sent
                    continue
                frame_to_send = frames[i]
                _, enc_frame = cv2.imencode(".jpg", frame_to_send, [int(cv2.IMWRITE_JPEG_QUALITY), 20])
                # TODO: perhaps, if success==False, should simply sent 0 model scores.
                is_final_frame = (s in self.__last_frame_hit and
                                  (len(frames) <= self.__batch_size) and
                                  (i + 1) == len(frames))
                if is_final_frame:
                    self.__to_delete.append(s)
                self.__on_done((s, frame_to_send, enc_frame, scores[j], not is_final_frame))

        # print('ML SENT BATCH')
        # self.print_batch_info()
        for s in self.__to_delete:
            # print('ML DELETED SOURCE.', {s})
            self.__remove_finished_source(s)
        self.__to_delete = []
        self.__reset_batches()

    def print_batch_info(self):
        for source_id in self.__batch_data.keys():
            print(f'source {source_id}, num_frames: {len(self.__batch_data[source_id]["frames"])}; ', end='')
        print()

    def __remove_finished_source(self, source_id: int) -> None:
        # print('ML, removing.')
        # self.print_batch_info()
        del self.__batch_data[source_id]
        self.__last_frame_hit.remove(source_id)
        # print('ML, after removing')
        # self.print_batch_info()

    def __reset_batches(self):
        self.__batch_data = {source_id: {'frames': data['frames'][self.__batch_size:],
                                         'ready': (len(data['frames'][self.__batch_size:]) >= self.__batch_size
                                                   or source_id in self.__last_frame_hit)}
                             for source_id, data in self.__batch_data.items()}

    def __infer(self) -> np.ndarray:
        input_tensor = self.__get_input_tensor()
        features = self.__feature_extractor_session.run(["output_0"], {"inputs": input_tensor})[0]
        reshaped_features = self.__reshape_input_for_transformer(features=features)
        return self.__transformer_session.run(["output_0"], {"inputs": reshaped_features})[0]

    def __reshape_input_for_transformer(self, features: np.ndarray) -> np.ndarray:
        batch_size = int(features.shape[0] / self.__batch_size)
        reshaped_features_shape = (batch_size, self.__batch_size, features.shape[1])
        reshaped_features = np.zeros(reshaped_features_shape, dtype=np.float32)
        for i in range(batch_size):
            reshaped_features[i] = features[i * self.__batch_size: i * self.__batch_size + self.__batch_size]
        return reshaped_features

    def __get_input_tensor(self):
        tensor = np.zeros((len(self.__batch_data) * self.__batch_size,
                           self.__img_h, self.__img_w, 3), dtype=np.float32)

        for i, source_id in enumerate(self.__batch_data.keys()):
            num_frames = (self.__batch_size if len(self.__batch_data[source_id]['frames']) > self.__batch_size else
                          len(self.__batch_data[source_id]['frames']))
            for j, frame in enumerate(self.__batch_data[source_id]['frames'][:num_frames]):
                resized_frame = cv2.resize(frame, (self.__img_h, self.__img_w))
                resized_frame = resized_frame[:, :, [2, 1, 0]]
                tensor[i * self.__batch_size + j] = resized_frame
        return tensor.astype(np.float32)

    def __set_batch_ready(self, source_id: int, success: bool) -> None:
        self.__batch_data[source_id]['ready'] = (not success or
                                                 len(self.__batch_data[source_id]['frames']) >= self.__batch_size or
                                                 source_id in self.__last_frame_hit)

    def __all_batches_ready(self):
        for source_id, data in self.__batch_data.items():
            if not data['ready']:
                return False

        return len(self.__batch_data) > 0
