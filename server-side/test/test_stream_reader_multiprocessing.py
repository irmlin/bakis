import queue
import time


class TestStreamReader:

    def test_add_source(self, mocked_stream_reader, video_source_to_read):
        q, stream_reader = mocked_stream_reader
        source_id, source_str = video_source_to_read

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 0

        stream_reader.add_source(source_id, source_str)

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 1

    def test_remove_source(self, mocked_stream_reader, video_source_to_read):
        q, stream_reader = mocked_stream_reader
        source_id, source_str = video_source_to_read

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 0

        stream_reader.add_source(source_id, source_str)

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 1

        stream_reader.remove_source(source_id)

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 0

    def test_output_queue_filled(self, mocked_stream_reader, video_source_to_read):
        q, stream_reader = mocked_stream_reader
        source_id, source_str = video_source_to_read
        stream_reader.add_source(source_id, source_str)

        time.sleep(1)
        try:
            data = q.get(timeout=1, block=True)
        except queue.Empty:
            assert 1 == 0, "No data put in queue!"

        s_id, frame, success = data
        assert s_id == source_id
        assert frame.size > 0
        assert success is True

    def test_after_reading_done(self, mocked_stream_reader, video_source_to_read):
        q, stream_reader = mocked_stream_reader
        source_id, source_str = video_source_to_read
        stream_reader.add_source(source_id, source_str)

        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 1

        time.sleep(20)
        with stream_reader.sources_lock:
            assert len(stream_reader.sources) == 0