import time

from tornado.gen import coroutine
import gemstone


class CoroutineService(gemstone.MicroService):
    name = "coroutine_service"

    @gemstone.async_method
    @gemstone.public_method
    def get_secret(self):
        secret = yield self._executor.submit(self.blocking_method)
        return secret

    def blocking_method(self):
        time.sleep(2)
        return 10


if __name__ == '__main__':
    service = CoroutineService()
    service.start()
