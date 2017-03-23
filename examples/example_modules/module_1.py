from gemstone.core.modules import Module
import gemstone


class FirstModule(Module):
    @gemstone.exposed_method("module1.say_hello")
    def say_hello(self):
        return "Hello from module 1!"
