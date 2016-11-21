import argparse

from pymicroservice.builtin.service_registry import ServiceRegistry
from pymicroservice.adapters.flask_adapter import FlaskJsonRpcAdapter

service_classes = {
    "registry": ServiceRegistry
}

adapters = {
    "flask": FlaskJsonRpcAdapter
}


def configure_builtin_service(args):
    service = service_classes.get(args.service_name)()

    adapter = adapters[args.adapter](args.host, args.port)
    service.add_adapter(adapter)
    return service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("service_name", choices=("registry",))
    parser.add_argument("--adapter", choices=("flask",), default="flask")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7777)

    args = parser.parse_args()
    service = configure_builtin_service(args)
    service.start()
