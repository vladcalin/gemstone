from unittest import TestCase
from unittest.mock import MagicMock, call
import threading
import time
from gemstone.auth.validation_strategies.header_strategy import HeaderValidationStrategy

from gemstone.client.remote_service import RemoteService, AsyncMethodCall
from gemstone import MicroService, public_method, private_api_method, as_completed, first_completed, make_callbacks
from gemstone.errors import CalledServiceError

HOST, PORT = "127.0.0.1", 6799
PORT2 = PORT + 1


class Service1(MicroService):
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
    def sleep(self, seconds):
        time.sleep(seconds)
        return seconds

    @public_method
    def sleep_with_error(self, seconds):
        time.sleep(seconds)
        raise ValueError(seconds)

    @public_method
    def method4(self, arg1, arg2):
        return {"arg1": arg1, "arg2": arg2}

    @private_api_method
    def method5(self, name):
        return "private {}".format(name)

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"


class Service2(MicroService):
    name = "test.service.client.2"

    validation_strategies = [
        HeaderValidationStrategy(header_name="Custom-Header")
    ]

    host = HOST
    port = PORT2

    @private_api_method
    def test(self):
        return True

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"


class ClientTestCase(TestCase):
    service_thread = None
    service_thread2 = None
    service_url = "http://127.0.0.1:6799/api"
    service_url2 = "http://127.0.0.1:6800/api"

    @classmethod
    def setUpClass(cls):
        service1 = Service1()
        service2 = Service2(io_loop=service1.io_loop)
        cls.service_thread = threading.Thread(target=service1.start, daemon=True)
        cls.service_thread.start()

        cls.service_thread2 = threading.Thread(target=service2.start, daemon=True)
        cls.service_thread2.start()

        time.sleep(1)  # wait for the servers to be ready to accept connections

    def test_client_connection(self):
        client = RemoteService(self.service_url)

        self.assertEqual(client.name, "test.service.client.1")
        self.assertCountEqual(client.get_available_methods(),
                              ["get_service_specs", "method1", "method2", "method3", "method4", "method5", "sleep",
                               "sleep_with_error"])

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

    def test_method_call_method_does_not_exist(self):
        client = RemoteService(self.service_url)
        with self.assertRaises(AttributeError):
            result = client.methods.does_not_exist()

    def test_method_call_wrong_params(self):
        client = RemoteService(self.service_url)
        with self.assertRaises(CalledServiceError):
            result = client.methods.method1(param="should_not_be_here")

        with self.assertRaises(CalledServiceError):
            result = client.methods.method1(1, 2, 3)

    def test_method_call_private_token_missing(self):
        client = RemoteService(self.service_url)  # no api token
        with self.assertRaises(CalledServiceError):
            result = client.methods.method5("test")

    def test_method_call_private_token_ok(self):
        client = RemoteService(self.service_url, options={"auth_type": "header", "auth_token": "test-token"})
        result = client.methods.method5("test")
        self.assertEqual(result, "private test")

    def test_method_call_private_token_incorrect(self):
        client = RemoteService(self.service_url, options={"auth_type": "header", "auth_token": "wrong-token"})
        with self.assertRaises(CalledServiceError):
            result = client.methods.method5("test")

    def test_method_call_custom_api_token_header(self):
        client = RemoteService(self.service_url2, options={"auth_type": "header", "auth_params": "Custom-Header",
                                                           "auth_token": "test-token"})
        result = client.methods.test()
        self.assertTrue(result)

    def test_notifications(self):
        client = RemoteService(self.service_url)
        response = client.notifications.method1()
        self.assertIsNone(response)

    def test_notifications_method_not_found(self):
        client = RemoteService(self.service_url)
        with self.assertRaises(AttributeError):
            response = client.notifications.does_not_exist()

    def test_notifications_bad_params(self):
        client = RemoteService(self.service_url)
        response = client.notifications.method1(1, 2, 3)
        self.assertTrue(response is None)  # every notification should return None because
        # do not care about the answer

    def test_async_single_call_valid_result(self):
        client = RemoteService(self.service_url)

        r = client.methods.method3(1, 2, __async=True)

        self.assertIsInstance(r, AsyncMethodCall)

        r.wait()

        self.assertEqual(r.result(), 3)
        self.assertIsNone(r.error())
        self.assertTrue(r.finished())

    def test_async_single_call_error(self):
        client = RemoteService(self.service_url)
        r = client.methods.method3("a", "b", __async=True)

        self.assertIsInstance(r, AsyncMethodCall)

        r.wait()

        self.assertIsNone(r.result())

        self.assertIsNotNone(r.error())
        self.assertEqual(r.error()["message"].lower(), "internal error")
        self.assertEqual(r.error()["code"], -32603)
        self.assertEqual(r.error()["data"]["class"], "ValueError")

        self.assertTrue(r.finished())

    def test_async_first_completed_async(self):
        client = RemoteService(self.service_url)

        requests = [client.methods.sleep(1 - x * 0.25, __async=True) for x in range(4)]
        first = first_completed(*requests)

        self.assertIsInstance(first, AsyncMethodCall)
        self.assertTrue(first in requests)

    def test_async_add_callbacks_main_thread(self):
        client = RemoteService(self.service_url)
        requests = [client.methods.sleep(1 - x * 0.25, __async=True) for x in range(4)]

        success_callback = MagicMock()
        fail_callback = MagicMock()

        make_callbacks(requests, on_result=success_callback, on_error=fail_callback)

        success_callback.assert_has_calls(
            [call(0.25), call(0.5), call(0.75), call(1.0)], any_order=True)
        fail_callback.assert_not_called()

    def test_async_add_callbacks_errors(self):
        client = RemoteService(self.service_url)
        requests = [client.methods.sleep_with_error(1 - x * 0.25, __async=True) for x in range(4)]

        success_callback = MagicMock()
        fail_callback = MagicMock()

        make_callbacks(requests, on_result=success_callback, on_error=fail_callback)

        success_callback.assert_not_called()

        # TODO: investigate to see why this part randomly fails
        #
        # call that causes the test to fail: call({'message': 'Internal error', 'data': {'info': '0.25', ...
        #
        # fail_callback.assert_has_calls([
        #     call({'message': 'Internal error', 'data': {'info': '0.25', 'class': 'ValueError'}, 'code': -32603}),
        #     call({'message': 'Internal error', 'data': {'info': '0.5', 'class': 'ValueError'}, 'code': -32603}),
        #     call({'message': 'Internal error', 'data': {'info': '0.75', 'class': 'ValueError'}, 'code': -32603}),
        #     call({'message': 'Internal error', 'data': {'info': '1.0', 'class': 'ValueError'}, 'code': -32603})
        # ], any_order=True)


