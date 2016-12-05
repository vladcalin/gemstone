from unittest import TestCase
import threading
import re

from pymicroservice.client.remote_service import RemoteService
from pymicroservice import PyMicroService, public_method
from pymicroservice.errors import CalledServiceError

HOST, PORT = "127.0.0.1", 6799


class Service1(PyMicroService):
    name = "test.service.client.1"

    host = HOST
    port = PORT

    @public_method
    def method1(self):
        return "hello there"

    @public_method
    def method2(self, arg):
        return "hello there {}".format(arg)

    @public_method
    def method3(self, a, b):
        if not isinstance(a, int) or not isinstance(b, int):
            raise ValueError("Bad type for a and b")
        return a + b

    @public_method
    def method4(self, arg1, arg2):
        return {"arg1": arg1, "arg2": arg2}


class ClientTestCase(TestCase):
    service_thread = None
    service_url = "http://127.0.0.1:6799/api"

    @classmethod
    def setUpClass(cls):
        cls.service_thread = threading.Thread(target=Service1().start, daemon=True)
        cls.service_thread.start()

    def test_client_connection(self):
        client = RemoteService(self.service_url)

        self.assertEqual(client.name, "test.service.client.1")
        self.assertCountEqual(client.get_available_methods(),
                              ["get_service_specs", "method1", "method2", "method3", "method4"])

    def test_method_call_no_args(self):
        client = RemoteService(self.service_url)

        result = client.methods.method1()
        self.assertEqual(result, "hello there")

    def test_method_call_with_args(self):
        client = RemoteService(self.service_url)

        result = client.methods.method2("hello")
        self.assertEqual(result, "hello there hello")

    def test_method_call_with_numeric_args(self):
        client = RemoteService(self.service_url)
        result = client.methods.method3(10, 11)
        self.assertEqual(result, 21)

        result = client.methods.method3(1, 1)
        self.assertEqual(result, 2)

        result = client.methods.method3(131, 33)
        self.assertEqual(result, 164)

        with self.assertRaisesRegex(CalledServiceError, "Bad type for a and b"):
            result = client.methods.method3("abc", "def")

    def test_method_call_with_complex_result(self):
        client = RemoteService(self.service_url)
        result = client.methods.method4(arg1="test", arg2="success")
        self.assertEqual(result, {"arg1": "test", "arg2": "success"})

        result = client.methods.method4("test", "success")
        self.assertEqual(result, {"arg1": "test", "arg2": "success"})


if __name__ == '__main__':
    Service1().start()
