from gemstone.auth.base.validation_strategy import BaseValidationStrategy


class BasicCookieStrategy(BaseValidationStrategy):
    def __init__(self, cookie_name="AuthToken", template=None):
        """

        Extracts the api token from a cookie. By default, tries to extract it from
        the ``'AuthToken'`` cookie

        :param cookie_name:
        :param template:

        ... versionadded:: 0.3.0

        """
        self.cookie = cookie_name
        if template:
            self.template = template
        else:
            self.template = lambda x: x

    def extract_api_token(self, request_handler):
        token = request_handler.get_cookie(self.cookie, default=None)
        return self.template(token)
