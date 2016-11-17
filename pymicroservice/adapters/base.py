from abc import ABC, abstractmethod


class BaseAdapter(ABC):

    @abstractmethod
    def register_endpoint(self, endpoint):
        """
        Registers a regular endpoint

        :param endpoint:
        :return:
        """
        pass

    @abstractmethod
    def serve(self):
        pass

