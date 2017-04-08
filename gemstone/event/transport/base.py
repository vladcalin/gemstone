from abc import ABC, abstractmethod


class BaseEventTransport(ABC):
    """
    Base class for defining event transports.

    The basic workflow would be the following:

    - the handlers are registered with the :py:meth:`BaseEventTransport.register_event_handler`
      method
    - the :py:meth:`BaseEventTransport.start_accepting_events` is invoked
    - for each incoming event, call :py:meth:`BaseEventTransport.on_event_received`
      whose responsibility is to invoke the proper handler function.

    """

    def __init__(self):
        self.microservice = None

    @abstractmethod
    def register_event_handler(self, handler_func, handled_event_name):
        """
        Registers a function to handle all events of type ``handled_event_name``

        :param handler_func: the handler function
        :param handled_event_name: the handled event type
        """
        pass

    @abstractmethod
    def start_accepting_events(self):
        """
        Starts accepting and handling events.
        """
        pass

    @abstractmethod
    def on_event_received(self, event_name, event_body):
        """
        Handles generic event. This function should treat every event that is received
        with the designated handler function.

        :param event_name: the name of the event to be handled
        :param event_body: the body of the event to be handled
        :return:
        """
        pass

    @abstractmethod
    def emit_event(self, event_name, event_body):
        """
        Emits an event of type ``event_name`` with the ``event_body`` content using the current
        event transport.

        :param event_name:
        :param event_body:
        :return:
        """
        pass

    def set_microservice(self, microservice):
        self.microservice = microservice

    def run_on_main_thread(self, func, args, kwargs):
        self.microservice.get_io_loop().add_callback(func, *args, **kwargs)
