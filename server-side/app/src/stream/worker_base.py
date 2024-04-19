import logging
import queue
import sys
import time
import traceback
from multiprocessing import Process, Queue, current_process

logger = logging.getLogger(__name__)


class WorkerBase:
    def __init__(self, max_q: int = 100) -> None:
        self._max_q = max_q
        self._queue: Queue = Queue()
        self._q_get_timeout = 1

    def add(self, d) -> None:
        if self._queue.qsize() > self._max_q:
            print(f'{current_process().name}: queue is full, queue size is {self._queue.qsize()}')
            return
        self._queue.put(d)

    def _do_work(self, data) -> None:
        raise NotImplementedError

    def __verbose_do_work(self, do_work_fn: callable) -> None:
        start_t = time.time()
        do_work_fn()
        logging.info(f'WORK_DONE: {round((time.time()-start_t)*1000, 3)}ms. {current_process().name}')

    def __process(self) -> None:
        print(f'Worker {current_process().name} is starting!')
        while 1:
            try:
                self._do_work(data=self._queue.get(timeout=self._q_get_timeout))
            except queue.Empty:
                continue
            except BaseException:
                e_type, e_object, e_traceback = sys.exc_info()
                logger.error(f'{current_process().name}:\nError:{e_type}:{e_object}\n'
                             f'{"".join(traceback.format_tb(e_traceback))}')

    def start(self) -> None:
        Process(target=self.__process).start()
