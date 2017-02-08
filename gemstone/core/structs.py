import simplejson as json


class JsonRpcResponse(object):
    def __init__(self, result=None, id=None, error=None):
        self.response = result
        self.id = id
        self.error = error

    def to_dict(self):
        to_return = {
            "jsonrpc": "2.0",
            "result": self.response,
            "error": self.error
        }
        if self.id:
            to_return["id"] = self.id
        return to_return

    def to_string(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return cls(
            response=d.get("response", None),
            error=d.get("error", None),
            id=d.get("id", None)
        )

    def __repr__(self):
        return "<JsonRpcResponse id={} response={} error={}>".format(self.id, self.response, self.error)


class JsonRpcRequest(object):
    def __init__(self, method=None, params=None, id=None, extra=None):
        self.method = method
        self.params = params or {}
        self.id = id
        self.extra = extra or {}
        self.invalid = False

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

    def to_string(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        """
        Validates a dict instance and transforms it in a :py:class:`gemstone.core.structs.JsonRpcRequest` instance

        :param d: The dict instance
        :return: A :py:class:`gemstone.core.structs.JsonRpcRequest` if everything goes well, or None if the validation
                 fails
        """
        for key in ("method", "jsonrpc"):
            if key not in d:
                instance = cls()
                instance.invalid = True
                return instance

        extra = {k: v for k, v in d.items() if k not in ("methods", "params", "id", "jsonrpc")}
        instance = cls(
            method=d.get("method"),
            params=d.get("params"),
            id=d.get("id"),
            extra=extra
        )
        if d["jsonrpc"] != "2.0":
            instance.invalid = True

        return instance

    def is_notification(self):
        return self.id is None

    def is_invalid(self):
        return self.invalid

    def __repr__(self):
        return "<JsonRpcRequest id={} method={} params={}>".format(self.id, self.method, self.params)


class JsonRpcRequestBatch(object):
    def __init__(self, *batch):
        self.batch_dict = {x.id: x for x in batch}

    def add_item(self, item, id=None):
        """Adds an item to the batch. If there is already another item
        with the same id, it will be overwritten"""
        item_id = id or item.id
        self.batch_dict[item_id] = item

    def to_list(self):
        return list(self.batch_dict.values())

    def to_string(self):
        return json.dumps(self.to_list())

    @classmethod
    def from_list(cls, l):
        return cls(*l)


class JsonRpcResponseBatch(object):
    def __init__(self, *batch):
        self.batch_dict = {x.id: x for x in batch}

    def add_item(self, item, id=None):
        """Adds an item to the batch. If there is already another item
        with the same id, it will be overwritten"""
        item_id = id or item.id
        self.batch_dict[item_id] = item

    def to_list(self):
        return list(self.batch_dict.values())

    def to_string(self):
        return json.dumps([i.to_dict() for i in self.to_list()])


class GenericResponse:
    PARSE_ERROR = JsonRpcResponse(error={"code": -32700, "message": "Parse error"})
    INVALID_REQUEST = JsonRpcResponse(error={"code": -32600, "message": "Invalid Request"})
    METHOD_NOT_FOUND = JsonRpcResponse(error={"code": -32601, "message": "Method not found"})
    INVALID_PARAMS = JsonRpcResponse(error={"code": -32602, "message": "Invalid params"})
    INTERNAL_ERROR = JsonRpcResponse(error={"code": -32603, "message": "Internal error"})
    ACCESS_DENIED = JsonRpcResponse(error={"code": -32001, "message": "Access denied"})

    NOTIFICATION_RESPONSE = JsonRpcResponse()
