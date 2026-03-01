# internal
from threading import Thread
from collections import deque
from multiprocessing import Event, Lock
import time
from functools import partial


class ThreadManager:
    className = 'ThreadManager'

    def __init__(self):
        super().__init__()  # for MRO

        self.thread = None
        self.thread_active = Event()
        self.thread_queue = deque()
        self.thread_queue_lock = Lock()

        self.thread_start()

    def thread_start(self):
        self.thread = Thread(
            name=f'{self.className}-Thread',
            target=self.thread_loop,
            daemon=True
        )
        self.thread_active.set()
        self.thread.start()

    def thread_loop(self):
        while self.thread_active.is_set():
            if not self.thread_queue:
                time.sleep(0.5)
            else:
                with self.thread_queue_lock:
                    current_func = self.thread_queue.popleft()
                current_func()

    def thread_add_worker(self, func, **kwargs):
        with self.thread_queue_lock:
            self.thread_queue.append(partial(func, **kwargs))
