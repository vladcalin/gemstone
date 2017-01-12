import os.path
import json
from unittest import TestCase

from tornado.testing import AsyncHTTPTestCase
from tornado.web import RequestHandler

from gemstone import MicroService, public_method
from gemstone.errors import ServiceConfigurationError

HOST, PORT = "127.0.0.1", 14777


class NameMissingService(MicroService):
    pass


class BadMaxParallelBlockingTasksValueService(MicroService):
    name = "test.1"
    max_parallel_blocking_tasks = -3


def get_static_dirs():
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_files")
    return [("/static", test_dir)]


def get_template_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_files")


class ExtraHandler1(RequestHandler):
    def get(self):
        self.render("template1.html")


class ExtraHandler2(RequestHandler):
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


class ServiceCreationTestCase(TestCase):
    def test_name_missing(self):
        with self.assertRaises(ServiceConfigurationError):
            NameMissingService().start()

    def test_max_parallel_blocking_tasks(self):
        with self.assertRaises(ServiceConfigurationError):
            BadMaxParallelBlockingTasksValueService().start()


class ServiceConfigurationTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return TestService2().make_tornado_app()

    def test_get_service_specs(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "get_service_specs"
        }
        resp = self.fetch("/api", method="POST", body=json.dumps(payload),
                          headers={"Content-Type": "application/json"})
        resp = json.loads(resp.body.decode())

        self.assertTrue(resp["id"] == 1)
        self.assertEqual(resp["result"]["host"], "127.0.0.1")
        self.assertEqual(resp["result"]["port"], 14777)
        self.assertEqual(resp["result"]["name"], "test.2")
        self.assertEqual(len(resp["result"]["methods"].keys()), 2)

    def test_get_static_file_1(self):
        resp = self.fetch("/static/static1")
        self.assertEqual(resp.body, b"this is static 1")

    def test_get_static_file_2(self):
        resp = self.fetch("/static/static2")
        self.assertEqual(resp.body, b"this is static 2")

    def test_get_static_outside_staticdir(self):
        resp = self.fetch("/static/../test_service_creation.py")
        self.assertEqual(resp.code, 403)
        self.assertTrue("forbidden" in resp.body.decode().lower())

    def test_render_template_1(self):
        resp = self.fetch("/tmp1")
        self.assertEqual(b"This is template 1", resp.body)

    def test_render_template_2(self):
        resp = self.fetch("/tmp2")
        self.assertEqual(b"hello world", resp.body)
