import gemstone
from gemstone.auth.validation_strategies import BasicCookieStrategy, HeaderValidationStrategy

VALIDATION_STRATEGIES = [
    HeaderValidationStrategy("X-Api-Token"),
    BasicCookieStrategy("AuthToken")
]


class ValidationStrategyTestService(gemstone.MicroService):
    name = "validation_strategy_test_service"
    port = 10090
    host = "127.0.0.1"

    validation_strategies = [
    ]

    @gemstone.private_api_method
    def private_echo(self, x):
        return x

    def api_token_is_valid(self, api_token):
        return api_token == "secret"

    def set_validation_strategy(self, validation_strategy):
        self.validation_strategies = [validation_strategy]
