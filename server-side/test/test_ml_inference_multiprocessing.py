import queue
import time

import cv2


class TestMLInference:
    def test_input_output_single_batch(self, mocked_ml_inference, video_source_to_read):
        batch_size, input_q, output_q, ml = mocked_ml_inference
        source_id, video_path = video_source_to_read

        cap = cv2.VideoCapture(video_path)
        for i in range(batch_size):
            success, frame = cap.read()
            ml.add((source_id, frame, success))

        time.sleep(1)

        for i in range(batch_size):
            try:
                s_id, frame, enc_frame, scores, success = output_q.get(timeout=1, block=True)
                assert s_id == source_id
                assert frame.size > 0
                assert len(enc_frame) > 0
                assert len(scores) == 2
                assert success is True
            except queue.Empty:
                assert 1 == 0, 'Output queue is empty!'
        cap.release()

    def test_input_output_not_full_batch(self, mocked_ml_inference, video_source_to_read):
        batch_size, input_q, output_q, ml = mocked_ml_inference
        source_id, video_path = video_source_to_read

        cap = cv2.VideoCapture(video_path)
        for i in range(batch_size-1):
            success, frame = cap.read()
            ml.add((source_id, frame, success))

        time.sleep(1)

        try:
            data = output_q.get(timeout=1, block=False)
            assert 1 == 0, 'Queue should have been empty!'
        except queue.Empty:
            pass

        cap.release()