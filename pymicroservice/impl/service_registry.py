import json
import sys
from argparse import ArgumentParser
import sqlite3
import importlib

from pymicroservice.core.microservice import PyMicroService
from pymicroservice.core.decorators import endpoint
from pymicroservice.adapters.flask_adapter import FlaskAdapter


class ServiceRegistry(PyMicroService):
    name = "pymicroservice.core.registry"

    def __init__(self, config_file):
        super(ServiceRegistry, self).__init__()

        with open(config_file, "r") as config_json:
            self.config = json.load(config_json)

        self.db = sqlite3.connect(self.config["db_location"])
        for adapter in self.config["adapters"]:
            class_name = adapter["class"]
            args = adapter["args"]
            kwargs = adapter["kwargs"]

            class_instance = self._get_class_by_name(class_name)
            self.add_adapter(class_instance(*args, **kwargs))

    @endpoint
    def register_service(self, name, location):
        pass

    @endpoint
    def unregister_service(self, name):
        pass

    @endpoint
    def locate_service(self, name):
        pass

    def _get_class_by_name(self, class_name):
        splitted = class_name.split(".")
        print(splitted)
        class_module, class_name = ".".join(splitted[:-1]), splitted[-1]
        print(class_module, class_name)
        module = importlib.import_module(class_module)
        print(module)
        return getattr(module, class_name)


def create_argparser():
    parser = ArgumentParser()
    parser.add_argument("config", default="service_registry.json")

    return parser


if __name__ == '__main__':
    parser = create_argparser()

    args = parser.parse_args(sys.argv[1:])
    registry = ServiceRegistry(args.config)
    registry.start()
