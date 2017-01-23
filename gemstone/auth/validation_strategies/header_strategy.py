from gemstone.auth.base.validation_strategy import BaseValidationStrategy


class HeaderValidationStrategy(BaseValidationStrategy):
    def __init__(self, header_name="X-Api-Token", template=None):
        """
        Extracts the api token from the HTTP headers. By defaults, tries
        to extract it from the ``X-Api-Token`` header.

        :param header_name: The name of the header. Defaults to ``"X-Api-Token"``
        :param template: A callable to be applied over the token. If not present, extracts the
                         token as it is.

       .. versionadded:: 0.3.0

        """
        self.header = header_name
        if template:
            self.template = template
        else:
            self.template = lambda x: x

    def extract_api_token(self, request_handler):
        token = request_handler.request.headers.get(self.header)
        return self.template(token)
