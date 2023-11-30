import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from skellysnapshot.backend.constants import TaskNames

import logging

class QueueManager:
    def __init__(self, num_workers):
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.active_threads = []  # Keep track of active worker threads
        self.stop_event = threading.Event()

    def add_task(self, task):
        self.task_queue.put(task)
        logging.info(f"Snapshot {task['id'] }added to queue. Queue size: {self.task_queue.qsize()}")


    def distribute_tasks(self):
        while not self.stop_event.is_set():
            task = self.task_queue.get()
            if task is None:  # Stop signal
                break

            # Process task if below worker limit, else wait
            if len(self.active_threads) < self.num_workers:
                logging.info(f"Sending snapshot {task['id']} to a thread worker. Active workers: {len(self.active_threads) + 1}. Queue size: {self.task_queue.qsize()}")
                worker = TaskWorkerThread(task)
                worker.start()
                self.active_threads.append(worker)
                worker.join()  # Optional: Only if you want to wait for each task to complete

            # Clean up completed threads
            self.active_threads = [t for t in self.active_threads if t.is_alive()]

            self.task_queue.task_done()

            before_cleanup = len(self.active_threads)
            self.active_threads = [t for t in self.active_threads if t.is_alive()]
            after_cleanup = len(self.active_threads)
            if before_cleanup != after_cleanup:
                logging.info(f"Cleaned up threads. Active workers: {after_cleanup}. Queue size: {self.task_queue.qsize()}")
