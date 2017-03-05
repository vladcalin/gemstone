import uuid
import gemstone


class TestMicroservice(gemstone.MicroService):
    name = "test"

    @gemstone.public_method
    @gemstone.requires_handler_reference
    def get_cookie(self, handler):
        return handler.get_cookie("Test", None)

    @gemstone.public_method
    @gemstone.requires_handler_reference
    def set_cookie(self, handler):
        handler.set_cookie("Test", str(uuid.uuid4()))
        return True


if __name__ == '__main__':
    service = TestMicroservice()
    service.start()
