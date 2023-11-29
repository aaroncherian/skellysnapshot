import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from skellysnapshot.backend.constants import TaskNames



class QueueManager:
    def __init__(self, num_workers):
        self.task_queue = queue.Queue()
        self.stop_event = threading.Event()

    def add_task(self, task):
        self.task_queue.put(task)

    def distribute_tasks(self):
        while not self.stop_event.is_set():
            task = self.task_queue.get()
            if task is None:  # Stop signal
                break
            self.process_task(task)
            self.task_queue.task_done()

    def process_task(self, task):
        worker = TaskWorkerThread(task)
        worker.start()
        worker.join() 