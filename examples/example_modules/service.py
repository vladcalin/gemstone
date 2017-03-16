import gemstone

from module_1 import FirstModule
from module_2 import SecondModule


class ModularizedMicroService(gemstone.MicroService):
    name = "module.example"
    host = "127.0.0.1"
    port = "8000"

    modules = [
        FirstModule(), SecondModule()
    ]


if __name__ == '__main__':
    ModularizedMicroService().start()
