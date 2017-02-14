import os.path
from unittest import TestCase

import simplejson as json
from tornado.testing import AsyncHTTPTestCase
from tornado.web import RequestHandler

from gemstone import MicroService, public_method
from gemstone.errors import ServiceConfigurationError

from tests.services.service_service_creation import NameMissingService, BadMaxParallelBlockingTasksValueService, \
    TestService2


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
