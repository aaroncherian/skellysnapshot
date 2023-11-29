import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from skellysnapshot.backend.constants import TaskNames



class QueueManager:
    def __init__(self, num_workers):
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.active_threads = []  # Keep track of active worker threads
        self.stop_event = threading.Event()

    def add_task(self, task):
        self.task_queue.put(task)

    def distribute_tasks(self):
        while not self.stop_event.is_set():
            task = self.task_queue.get()
            if task is None:  # Stop signal
                break

            # Process task if below worker limit, else wait
            if len(self.active_threads) < self.num_workers:
                worker = TaskWorkerThread(task)
                worker.start()
                self.active_threads.append(worker)
                # worker.join()  # Optional: Only if you want to wait for each task to complete

            # Clean up completed threads
            self.active_threads = [t for t in self.active_threads if t.is_alive()]

            self.task_queue.task_done()
