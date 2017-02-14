from unittest import TestCase, skipIf
from unittest.mock import patch
from io import BytesIO
import sys

from tests.services.service_service_registry_integration import TestServiceNoServiceRegistries, \
    TestServiceOneServiceRegistry

IS_WINDOWS = sys.platform.startswith("win32")


class ServiceRegistryIntegrationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @patch("gemstone.core.microservice.PeriodicCallback")
    @patch("urllib.request.urlopen")
    @skipIf(IS_WINDOWS, "different default callbacks for windows")
    def test_periodic_callback_init(self, urlopen, PeriodicCallback):
        callbacks = list(TestServiceNoServiceRegistries()._periodic_task_iter())
        self.assertEqual(len(callbacks), 0)
        urlopen.assert_not_called()

        urlopen.return_value = BytesIO(b'{"result":{"name":"registry", "methods":'
                                       b'{"ping": "", "locate_service": ""}}}')

        callbacks = list(TestServiceOneServiceRegistry()._periodic_task_iter())
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(urlopen.call_count, 2)  # get_service_specs and initial ping
