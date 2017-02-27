import os.path

from tornado.web import RequestHandler

from gemstone import MicroService, public_method
from gemstone.core.handlers import GemstoneCustomHandler


class NameMissingService(MicroService):
    pass


class BadMaxParallelBlockingTasksValueService(MicroService):
    name = "test.1"
    max_parallel_blocking_tasks = -3


def get_static_dirs():
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_files")
    return [("/static", test_dir)]


HOST, PORT = "127.0.0.1", 14777


def get_template_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_files")


class ExtraHandler1(GemstoneCustomHandler):
    def get(self):
        self.render("template1.html")


class ExtraHandler2(GemstoneCustomHandler):
    def get(self):
        self.render("template2.html", name="world")


class TestService2(MicroService):
    name = "test.2"
    host = HOST
    port = PORT

    static_dirs = get_static_dirs()
    template_dir = get_template_dir()

    extra_handlers = [
        (r"/tmp1", ExtraHandler1),
        (r"/tmp2", ExtraHandler2)
    ]

    @public_method
    def say_hello(self, who):
        return "hello " + who
