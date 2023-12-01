import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from skellysnapshot.backend.constants import TaskNames
from concurrent.futures import ThreadPoolExecutor


import logging
import time


class QueueManager:
    def __init__(self, num_workers):
        start_time = time.time()
        self.task_queue = queue.Queue()
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        init_time = time.time() - start_time
        logging.info(f"ThreadPoolExecutor initialization time: {init_time} seconds")

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
            start_time = time.time()
            future = self.executor.submit(processor.process_tasks)
            submit_time = time.time() - start_time
            logging.info(f"Time to submit Snapshot {task['id']}: {submit_time} seconds")

            self.active_tasks.add(future)
            future.add_done_callback(lambda f: self.task_done_callback(f, task['id']))


            self.task_queue.task_done()

    def task_done_callback(self, future, task_id):
        if future.exception() is not None:
            logging.error(f"Snapshot {task_id} resulted in an error: {future.exception()}")
        else:
            logging.info(f"Snapshot {task_id} completed")
        self.active_tasks.remove(future)

    def stop(self):
        # Add a stop signal to the queue
        self.task_queue.put(None)
        # Wait for all tasks in the queue to be processed
        self.task_queue.join()
        # Shutdown the executor
        self.executor.shutdown(wait=True)