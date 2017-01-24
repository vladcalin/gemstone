import json
import code
import traceback
import signal

# import pystuck; pystuck.run_server()

from tornado.testing import AsyncHTTPTestCase

from gemstone import MicroService, public_method, private_api_method
from gemstone.auth.validation_strategies.header_strategy import HeaderValidationStrategy
from gemstone.auth.validation_strategies.basic_cookie_strategy import BasicCookieStrategy

TEST_HOST, TEST_PORT = ("localhost", 65503)


class TestService(MicroService):
    name = "service.test.2"

    host = TEST_HOST
    port = TEST_PORT

    validation_strategies = [
        HeaderValidationStrategy(header_name="X-Testing-Token")
    ]

    @public_method
    def test1(self):
        return "test1_ok"

    @public_method
    def test2(self, arg1, arg2):
        return arg1 + arg2

    @private_api_method
    def test3(self, msg):
        return {
            "response": msg
        }

    @public_method
    def test_raises(self):
        raise ValueError("This is a test")

    def api_token_is_valid(self, api_token):
        return api_token == "testing_token"


class TestServiceWithCookieAuth(MicroService):
    name = "service.test.3"
    host = TEST_HOST
    port = TEST_PORT + 1

    validation_strategies = [
        BasicCookieStrategy(cookie_name="AuthToken")
    ]

    @private_api_method
    def test(self, arg):
        return arg

    def api_token_is_valid(self, api_token):
        return api_token == "test_ok"


class PyMicroServiceBehaviourTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return TestService().make_tornado_app()

    def test_public_method_call(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test1",
            "id": 1
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json"})
        response = json.loads(response.body.decode())

        self.assertEqual(response["result"], "test1_ok")
        self.assertEqual(response["error"], None)
        self.assertEqual(response["id"], 1)

    def test_private_method_call_no_api_token_header(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test3",
            "id": 1,
            "params": {"msg": "test"}
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json"})
        response = json.loads(response.body.decode())

        self.assertEqual(response["result"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["message"].lower(), "access denied")

    def test_private_method_call_bad_api_token(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test3",
            "id": 1,
            "params": {"msg": "test"}
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json",
                                       "X-Testing-Token": "bad_token"})
        response = json.loads(response.body.decode())

        self.assertEqual(response["result"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["message"].lower(), "access denied")

    def test_private_method_call_good_token(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test3",
            "id": 1,
            "params": {"msg": "test"}
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json",
                                       "X-Testing-Token": "testing_token"})
        response = json.loads(response.body.decode())

        self.assertIsNotNone(response["result"])
        self.assertEqual(response["result"]["response"], "test")
        self.assertEqual(response["id"], 1)
        self.assertIsNone(response["error"])

    def test_public_method_call_which_raises_exception(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test_raises",
            "id": 77
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json"})
        response = json.loads(response.body.decode())
        self.assertEqual(response["result"], None)
        self.assertEqual(response["error"]["code"], -32603)
        self.assertEqual(response["error"]["message"].lower(), "internal error")
        self.assertEqual(response["error"]["data"], {"class": "ValueError", "info": "This is a test"})
        self.assertEqual(response["id"], 77)


class TestCaseServiceWithCookieAuth(AsyncHTTPTestCase):
    def get_app(self):
        return TestServiceWithCookieAuth().make_tornado_app()

    def test_no_cookie_sent(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {
                "arg": "ok"
            },
            "id": 1
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json"})  # no 'Cookie: ApiToken=...'
        response = json.loads(response.body.decode())
        self.assertEqual(response["result"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["message"].lower(), "access denied")

    def test_bad_cookie_sent(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {
                "arg": "ok"
            },
            "id": 1
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json", "Cooke": "SomeCookie=Irrelevant"})
        response = json.loads(response.body.decode())
        self.assertEqual(response["result"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["message"].lower(), "access denied")

    def test_bad_cookie_value(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {
                "arg": "ok"
            },
            "id": 1
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json", "Cooke": "AuthToken=BadCookie"})
        response = json.loads(response.body.decode())
        self.assertEqual(response["result"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["error"]["code"], -32001)
        self.assertEqual(response["error"]["message"].lower(), "access denied")

    def test_ok_cookie_value(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {
                "arg": "ok"
            },
            "id": 1
        }
        response = self.fetch("/api", method="POST", body=json.dumps(payload),
                              headers={"Content-Type": "application/json", "Cookie": "AuthToken=test_ok"})
        response = json.loads(response.body.decode())
        self.assertEqual(response["error"], None)
        self.assertEqual(response["id"], 1)
        self.assertEqual(response["result"], "ok")
