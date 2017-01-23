from gemstone.auth.base.validation_strategy import BaseValidationStrategy


class HeaderValidationStrategy(BaseValidationStrategy):
    def __init__(self, header_name, template=None):
        self.header = header_name
        if template:
            self.template = template
        else:
            self.template = lambda x: x

    def extract_api_token(self, request_handler):
        token = request_handler.request.headers.get(self.header)
        return self.template(token)
