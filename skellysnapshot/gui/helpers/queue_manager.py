import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from skellysnapshot.backend.constants import TaskNames
from concurrent.futures import ThreadPoolExecutor


import logging

class QueueManager:
    def __init__(self, num_workers):
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.active_tasks = set()

    def add_task(self, task):
        # Add task to the queue and log it
        self.task_queue.put(task)
        logging.info(f"Snapshot {task['id']} added to queue. Queue size: {self.task_queue.qsize()}")

    def distribute_tasks(self):
        while True:
            task = self.task_queue.get()
            if task is None:  # Stop signal
                break

            logging.info(f"Sending snapshot {task['id']} for processing. Queue size: {self.task_queue.qsize()}")
            processor = TaskWorkerThread(task)
            future = self.executor.submit(processor.process_tasks)
            self.active_tasks.add(future)
            future.add_done_callback(lambda f: self.active_tasks.remove(f))

            self.task_queue.task_done()

    def stop(self):
        # Add a stop signal to the queue
        self.task_queue.put(None)
        # Wait for all tasks in the queue to be processed
        self.task_queue.join()
        # Shutdown the executor
        self.executor.shutdown(wait=True)