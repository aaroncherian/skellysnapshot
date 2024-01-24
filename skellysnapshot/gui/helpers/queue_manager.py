import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorker
# from concurrent.futures import ThreadPoolExecutor
import logging

import queue
import threading

import multiprocessing


from PySide6.QtCore import QObject, Signal

def task_worker_function(task_queue, results_queue, init_params):
    # Initialize the TaskWorker with provided initialization parameters
    worker = TaskWorker(init_params)

    while True:
        # Wait for a new task; block if the queue is empty
        frame_data = task_queue.get()

        # Check for the sentinel value to shut down the worker
        if frame_data is None:
            break

        # Process the frame and put the result in the results queue
        result = worker.process_snapshot(frame_data)
        results_queue.put(result)

class QueueManager(QObject):
    task_completed = Signal(dict)

    def __init__(self, max_concurrent_tasks):
        super().__init__()
        self.task_queue = multiprocessing.Queue()
        self.results_queue = multiprocessing.Queue()
        self.workers = []
        self.max_concurrent_tasks = max_concurrent_tasks

    def initialize_workers(self, init_params):
        for _ in range(self.max_concurrent_tasks):
            p = multiprocessing.Process(target=task_worker_function, args=(self.task_queue, self.results_queue, init_params))
            p.start()
            self.workers.append(p)
        logging.info("Worker processes initialized.")

    def add_task(self, task):
        self.task_queue.put(task)
        logging.info(f"Task {task['id']} added to queue.")

    def check_completed_tasks(self):
        while not self.results_queue.empty():
            result = self.results_queue.get()
            self.task_completed.emit(result)
            logging.info(f"Task {result['id']} completed.")

    def stop(self):
        for _ in self.workers:
            self.task_queue.put(None)
        for worker in self.workers:
            worker.join()
        self.task_queue.close()
        self.results_queue.close()
        logging.info("Worker processes stopped.")