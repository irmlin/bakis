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

from ..ml import PickableInferenceSession


class WorkerMLInference:
    def __init__(self, on_done: callable, batch_size: int = 5, img_h: int = 128, img_w: int = 128) -> None:
        self.__queue = multiprocessing.Queue(maxsize=500)
        self.__session = PickableInferenceSession(
            model_path='/home/irmantas/Desktop/bakis/data_prep/output/transformer/video_classifier_every_2nd.onnx')
        self.__on_done = on_done
        self.__batch_size = batch_size
        self.__img_h = img_h
        self.__img_w = img_w
        self.__batch_data: Dict[int, Dict[str, Any]] = {}
        self.__last_frame_hit = []
        self.__to_delete = []
        self.__feature_extractor_onnx_path = 'app/src/ml/models/feature_extractor_gpu.onnx'
        self.__transformer_onnx_path = 'app/src/ml/models/transformer_gpu.onnx'
        print(os.getcwd())
        self.__feature_extractor_session = PickableInferenceSession(self.__feature_extractor_onnx_path)
        self.__transformer_session = PickableInferenceSession(self.__transformer_onnx_path)

    def add(self, data) -> None:
        try:
            self.__queue.put(data, block=True)
        except queue.Full:
            print(f'WorkerMLInference queue is full! Element not added.')
            return

    def start(self) -> None:
        Process(target=self.__do_work, name='PROCESS_worker_ml_inference').start()

    def __do_work(self) -> None:
        while 1:
            try:
                # TODO: timeout
                source_id, frame, success, frame_num = self.__queue.get(block=True, timeout=0.1)
                if source_id not in self.__batch_data.keys():
                    # Initialize new source
                    self.__batch_data[source_id] = {'frames': [], 'ready': False, 'frame_nums': []}

                if success:
                    self.__batch_data[source_id]['frames'].append(frame)
                    self.__batch_data[source_id]['frame_nums'].append(frame_num)
                else:
                    self.__last_frame_hit.append(source_id)

                self.__set_batch_ready(source_id, success)

                if not self.__all_batches_ready():
                    continue

                # scores = self.__infer()
                scores = np.random.rand(len(self.__batch_data), 2)
                # print(scores)
                for i in range(self.__batch_size):
                    for j, s in enumerate(self.__batch_data.keys()):
                        frames = self.__batch_data[s]['frames']
                        if i >= len(frames):
                            # All frames have been sent
                            continue
                        fn = self.__batch_data[s]['frame_nums'][i]
                        _, enc_frame = cv2.imencode(".jpg", frames[i], [int(cv2.IMWRITE_JPEG_QUALITY), 20])
                        # TODO: perhaps, if success==False, should simply sent 0 model scores.
                        is_final_frame = (s in self.__last_frame_hit and
                                          (len(frames) <= self.__batch_size) and
                                          (i + 1) == len(frames))
                        if is_final_frame:
                            self.__to_delete.append(s)
                        self.__on_done((s, enc_frame, scores[j], not is_final_frame, fn))

                for s in self.__to_delete:
                    self.__remove_finished_source(s)
                self.__to_delete = []
                self.__reset_batches()

            except queue.Empty:
                pass
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{current_process().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    def __remove_finished_source(self, source_id: int) -> None:
        del self.__batch_data[source_id]
        self.__last_frame_hit.remove(source_id)

    def __reset_batches(self):
        self.__batch_data = {source_id: {'frames': data['frames'][self.__batch_size:],
                                         'ready': (len(data['frames'][self.__batch_size:]) >= self.__batch_size
                                                   or source_id in self.__last_frame_hit),
                                         'frame_nums': data['frame_nums'][self.__batch_size:]}
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
            for j, frame in enumerate(self.__batch_data[source_id]['frames']):
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
        return True
