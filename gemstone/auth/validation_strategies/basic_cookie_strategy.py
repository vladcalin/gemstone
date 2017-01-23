from gemstone.auth.base.validation_strategy import BaseValidationStrategy


class BasicCookieStrategy(BaseValidationStrategy):
    def __init__(self, cookie_name="AuthToken", template=None):
        self.cookie = cookie_name
        if template:
            self.template = template
        else:
            self.template = lambda x: x

    def extract_api_token(self, request_handler):
        token = request_handler.get_cookie(self.cookie, default=None)
        return self.template(token)
