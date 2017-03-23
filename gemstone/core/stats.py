import time
from threading import Lock


class DummyStatsContainer(object):
    def as_json(self):
        return {}

    def after_method_call(self, *args, **kwargs):
        pass


class DefaultStatsContainer(object):
    def __init__(self):
        self.lock = Lock()

        self.method_calls_count = 0
        self.method_calls = {}
        self.service_start = time.time()

    def after_method_call(self, method, duration, is_error=False):
        with self.lock:
            self.method_calls_count += 1

            self.method_calls.setdefault(method, {
                "total_calls": 0,
                "average_resp_time": 0,
                "success_calls": 0,
                "failed_calls": 0
            })
            if is_error:
                self.method_calls[method]["failed_calls"] += 1
            else:
                self.method_calls[method]["success_calls"] += 1

            method_stats = self.method_calls[method]
            self.method_calls[method]["average_resp_time"] = (method_stats["average_resp_time"] *
                                                              method_stats[
                                                                  "total_calls"] + duration) / (
                                                                 method_stats["total_calls"] + 1)
            self.method_calls[method]["total_calls"] += 1

    def as_json(self):
        with self.lock:
            return {
                "total_runtime": time.time() - self.service_start,
                "method_calls_count": self.method_calls_count,
                "method_calls": self.method_calls
            }
