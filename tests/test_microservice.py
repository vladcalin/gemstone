from tornado.testing import AsyncHTTPTestCase
import simplejson as json

from tests.services.service_microservice import TestService, TestServiceWithCookieAuth


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
