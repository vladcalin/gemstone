import string
import random


class MethodCall(object):
    def __init__(self, method_name, params=None, id=None):
        self.method_name = method_name
        self.params = params or {}
        self.id = id or self._generate_id()

    def _generate_id(self):
        return "".join([random.choice(string.ascii_letters) for _ in range(10)])

    def __repr__(self):
        return "MethodCall(id={}, method_name={}, params={})".format(self.id, self.method_name,
                                                                     self.params)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, MethodCall):
            return False

        return hash(self) == hash(other)


class Notification(object):
    def __init__(self, method_name, params=None, id=None):
        self.method_name = method_name
        self.params = params or {}
        self.id = None

    def __repr__(self):
        return "Notification(method_name={}, params={})".format(self.method_name, self.params)


class Result(object):
    def __init__(self, result, error, id, method_call):
        self.result = result
        self.error = error
        self.id = id
        self.method_call = method_call

    def __repr__(self):
        return "Response(result={}, error={}, id={}, method_call={})".format(
            self.result, self.error, self.id, self.method_call
        )


class BatchResult(object):
    def __init__(self, *responses):
        self.responses = list(responses)

    def add_response(self, response):
        self.responses.append(response)

    def __iter__(self):
        return iter(self.responses)

    def get_response_for_call(self, method_call):
        items = [x for x in self.responses if x.method_call == method_call]
        if not items:
            return None
        else:
            return items[0]


class AsyncMethodCall(object):
    def __init__(self):
        pass

    def is_ready(self):
        pass

    def result(self):
        pass

    def get(self):
        pass

    def successful(self):
        pass

    def reraise(self):
        pass
