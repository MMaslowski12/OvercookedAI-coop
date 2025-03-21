from concurrent.futures import ThreadPoolExecutor

class Thread:
    def __init__(self, type, future):
        self.type = type
        self.future = future

class APIThreadManager:
    def __init__(self, max_workers=1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.threads_number = 0
        self.threads = {}

    def add_thread(self, func, type, *args, **kwargs):
        """
        Submits a task to the executor and stores its thread.
        Returns a Thread object.
        """
        future = self.executor.submit(func, *args, **kwargs)
        thread = Thread(type, future)
        self.threads[future] = thread
        self.threads_number += 1
        return thread

    def is_done(self, thread):
        """
        Checks if the given thread is complete.
        Returns True if done, False otherwise.
        """
        return thread.future.done()

    def get_result(self, thread):
        """
        Retrieves the result from a completed thread.
        Blocks until the result is ready, if necessary.
        """
        return thread.future.result()

    def remove_thread(self, thread):
        """
        Removes the thread from tracking once it's processed.
        """
        if thread.future in self.threads:
            del self.threads[thread.future]
            self.threads_number -= 1