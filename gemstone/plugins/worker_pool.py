import os
from multiprocessing import Pool

from tornado.gen import coroutine, sleep

from .base import BasePlugin


class MultiProcessingWorkerPoolPlugin(BasePlugin):
    """

    Initialization

    ::

        service.register_plugin(MultiProcessingWorkerPoolPlugin())

    Usage


    ::
        # synchronously run job in an asynchronously manner
        res = yield self.get_plugin("mp-worker-pool").submit(compute_fibbonacci, kwargs={"n": 100})

        # asynchronously run job in an asynchronously manner
        res = yield self.get_plugin("mp-worker-pool").submit_async(compute_fibbonacci, kwargs={"n": 100})


    """

    name = "mp-worker-pool"

    def __init__(self, worker_count=os.cpu_count(), pool_class=Pool, restart_worker_after_jobs=None):
        self.worker_count = worker_count
        self.pool_class = pool_class
        self.restart_worker_after_jobs = restart_worker_after_jobs

        self.pool = None

        super(MultiProcessingWorkerPoolPlugin, self).__init__()

    def on_service_start(self):
        self.pool = self.pool_class(self.worker_count, maxtaskperchild=self.restart_worker_after_jobs)

    def on_service_stop(self):
        self.pool.close()

    # extra methods

    @coroutine
    def submit(self, func, args, kwargs):
        async_res = self.pool.apply_async(func, args, kwargs)
        while not async_res.ready():
            yield sleep(0.1)
        return async_res.get()

