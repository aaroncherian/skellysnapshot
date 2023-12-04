import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from threading import Semaphore
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Semaphore

class QueueManager:
    def __init__(self, max_concurrent_tasks):
        self.task_queue = queue.Queue()
        self.semaphore = Semaphore(max_concurrent_tasks)
        self.executor = ThreadPoolExecutor()
        self.active_tasks = set()

    def add_task(self, task):
        self.task_queue.put(task)
        logging.info(f"Task {task['id']} added to queue by thread {threading.get_ident()}. Queue size: {self.task_queue.qsize()}")

    def distribute_tasks(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break

            logging.info(f"Thread {threading.get_ident()} attempting to acquire semaphore for task {task['id']}...")
            self.semaphore.acquire()
            logging.info(f"Semaphore acquired for task {task['id']} by thread {threading.get_ident()}. Submitting to executor.")

            processor = TaskWorkerThread(task)
            future = self.executor.submit(processor.process_tasks)
            self.active_tasks.add(future)
            future.add_done_callback(lambda f, task_id=task['id']: self.task_done_callback(f, task_id))

    def task_done_callback(self, future, task_id):
        self.semaphore.release()
        logging.info(f"Semaphore released for task {task_id} by thread {threading.get_ident()}.")
        if future.exception() is not None:
            logging.error(f"Task {task_id} resulted in an error: {future.exception()}")
        else:
            logging.info(f"Task {task_id} completed successfully.")
        self.active_tasks.remove(future)
        self.task_queue.task_done()

    def stop(self):
        self.task_queue.put(None)
        self.task_queue.join()
        self.executor.shutdown(wait=True)
