import abc


class BaseValidationStrategy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def extract_api_token(self, request_handler):
        """
        Given a Tornado Request handler object, extracts the api token required for validation,
        which will be passed to :py:meth:`MicroService.api_token_is_valid`

        :param request_handler: a :py:class:`tornado.web.RequestHandler` that handles the current request
        :return:
        """
        pass
