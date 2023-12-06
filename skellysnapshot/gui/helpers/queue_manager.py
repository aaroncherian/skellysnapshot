import queue
import threading
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread
# from concurrent.futures import ThreadPoolExecutor
import logging
import time
from threading import Semaphore
import queue
import threading


from concurrent.futures import ProcessPoolExecutor
from threading import Semaphore

from PySide6.QtCore import QObject, Signal

def task_worker_function(task):
    worker = TaskWorkerThread(task)
    return worker.process_tasks()


class QueueManager(QObject):
    task_completed = Signal()

    def __init__(self, max_concurrent_tasks):
        super().__init__()
        self.task_queue = queue.Queue()
        self.semaphore = Semaphore(max_concurrent_tasks)
        self.executor = ProcessPoolExecutor(max_workers=max_concurrent_tasks)
        self.active_tasks = set()
        self.completed_tasks = queue.Queue()  # Assuming you need this for completed tasks


    def add_task(self, task):
        self.task_queue.put(task)
        logging.info(f"Task {task['id']} added to queue. Queue size: {self.task_queue.qsize()}")

    def distribute_tasks(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break

            self.semaphore.acquire()
            logging.info(f"Semaphore acquired for task {task['id']}. Submitting to executor.")
            future = self.executor.submit(task_worker_function, task)
            self.active_tasks.add(future)
            future.add_done_callback(lambda f, task_id=task['id']: self.task_done_callback(f, task_id))

    def task_done_callback(self, future, task_id):
        self.semaphore.release()
        logging.info(f"Semaphore released for task {task_id}.")
        
        if future.exception() is not None:
            logging.error(f"Task {task_id} resulted in an error: {future.exception()}")
        else:
            logging.info(f"Task {task_id} completed successfully.")
            # Optionally, you can add the result to a completed tasks queue here
            # if you need to process the results further
            self.completed_tasks.put(future.result())

        # Remove the completed task from active_tasks
        self.active_tasks.remove(future)

        # Emit signal that a task is done
        self.task_completed.emit()

        self.task_queue.task_done()

    def stop(self):
        self.task_queue.put(None)
        self.task_queue.join()
        self.executor.shutdown(wait=True)
