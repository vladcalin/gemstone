import random
import datetime

from gemstone import MicroService, exposed_method, GemstoneCustomHandler


class IndexHandler(GemstoneCustomHandler):
    def get(self):
        self.render("index.html")


class VueJsExample(MicroService):
    name = "example.vue_js"

    host = "127.0.0.1"
    port = 8000

    template_dir = "."
    static_dirs = [("/static", ".")]

    extra_handlers = [
        (r"/", IndexHandler)
    ]

    @exposed_method()
    def get_user_info(self):
        return random.choice([{
            "username": "admin",
            "email": "admin@example.org",
            "last_seen": str(datetime.datetime.now())
        }, {
            "username": "admin2",
            "email": "admin2@example.org",
            "last_seen": str(datetime.datetime.now())
        }, {
            "username": "admin3",
            "email": "admin3@example.org",
            "last_seen": str(datetime.datetime.now())
        }])


if __name__ == '__main__':
    service = VueJsExample()
    service.configure()

    print(service.port)
    print(service.host)
    service.start()
