class JsonRpcResponse(object):
    def __init__(self, response=None, id=None, error=None):
        self.response = response
        self.id = id
        self.error = error

    def to_dict(self):
        return {
            "id": self.id,
            "jsonrpc": "2.0",
            "response": self.response,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            response=d.get("response", None),
            error=d.get("error", None),
            id=d.get("id", None)
        )


class JsonRpcRequest(object):
    def __init__(self, method=None, params=None, id=None, extra=None):
        self.method = method
        self.params = params or {}
        self.id = id
        self.extra = extra or {}

    def to_dict(self):
        to_ret = {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params,
            "id": self.id
        }
        for k, v in self.extra.items():
            to_ret[k] = v
        return to_ret

    @classmethod
    def from_dict(cls, d):
        extra = {k: v for k, v in d.items() if k not in ("methods", "params", "id", "jsonrpc")}
        instance = cls(
            method=d.get("method"),
            params=d.get("params"),
            id=d.get("id"),
            extra=extra
        )
        return instance

    def is_notification(self):
        return self.id is None


class JsonRpcRequestBatch(object):
    def __init__(self, *batch):
        self.batch = batch


class JsonRpcResponseBatch(object):
    def __init__(self, *batch):
        self.batch = batch
