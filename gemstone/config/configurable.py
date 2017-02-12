import abc


class Configurable(abc.ABC):
    @abc.abstractmethod
    def value(self):
        pass

    @abc.abstractmethod
    def set_value(self, value):
        pass

    @abc.abstractmethod
    def is_set(self):
        pass


class Required(Configurable):
    def __int__(self, *, mapping=None):
        self.mapping = mapping or {}
        self._value = None
        self._is_set = False

    def set_value(self, value):
        self._value = value
        self._is_set = True

    def is_set(self):
        return self._is_set

    def value(self):
        template = self.mapping.get(self._value)
        if not template:
            return self._value
        else:
            return template(self._value)


class Optional(Configurable):
    def __init__(self, default, *, mapping=None):
        self.mapping = mapping or {}
        self._value = default

    def set_value(self, value):
        self._value = value

    def value(self):
        template = self.mapping.get(self._value)
        if not template:
            return self._value
        else:
            return template(self._value)

    def is_set(self):
        return True
