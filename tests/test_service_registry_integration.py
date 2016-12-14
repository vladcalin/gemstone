from unittest import TestCase
from unittest.mock import patch
from io import BytesIO

from pymicroservice import PyMicroService


class TestServiceNoServiceRegistries(PyMicroService):
    name = "test.service.1"


class TestServiceOneServiceRegistry(PyMicroService):
    name = "test.service.1"
    service_registry_urls = ["http://localhost:9999/api"]


class ServiceRegistryIntegrationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @patch("pymicroservice.core.microservice.PeriodicCallback")
    @patch("urllib.request.urlopen")
    def test_periodic_callback_init(self, urlopen, PeriodicCallback):
        callbacks = list(TestServiceNoServiceRegistries().periodic_task_iter())
        self.assertEqual(len(callbacks), 0)
        urlopen.assert_not_called()

        urlopen.return_value = BytesIO(b'{"result":{"name":"registry", "methods":'
                                       b'{"ping": "", "locate_service": ""}}}')

        callbacks = list(TestServiceOneServiceRegistry().periodic_task_iter())
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(urlopen.call_count, 2)  # get_service_specs and initial ping
