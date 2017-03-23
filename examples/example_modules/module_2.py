from gemstone.core.modules import Module
import gemstone


class SecondModule(Module):
    @gemstone.exposed_method("module2.say_hello")
    def say_hello(self):
        return "Hello from module 2!"
