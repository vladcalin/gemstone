import time

import gemstone


class TestMicroservice(gemstone.MicroService):
    name = "test"

    @gemstone.exposed_method('say_hello', public=True)
    def hello_world(self, x):
        return "hello " + x

    @gemstone.exposed_method('math.add_anything')
    def do_internal_stuff(self, a, b):
        return a + b

    @gemstone.exposed_method()
    def stuff(self):
        return ":)"

    @gemstone.exposed_method('stuff.2')
    def stuff2(self):
        return ":("

    @gemstone.exposed_method('slow_method', is_coroutine=True)
    def slow_stuff_happening_here(self):
        x = yield self._executor.submit(self.slow_method)
        print(x)
        return x

    def slow_method(self):
        time.sleep(2)
        return 10


if __name__ == '__main__':
    service = TestMicroservice()
    service.start()
