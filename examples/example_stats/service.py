import gemstone


class StatsService(gemstone.MicroService):
    name = "stats_example"
    port = 8000

    use_statistics = True

    @gemstone.exposed_method()
    def sum(self, a, b):
        return a + b


if __name__ == '__main__':
    StatsService().start()
