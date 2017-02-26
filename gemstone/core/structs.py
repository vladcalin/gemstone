import simplejson as json


class JsonRpcError(Exception):
    pass


class JsonRpcParseError(JsonRpcError):
    pass


class JsonRpcInvalidRequestError(JsonRpcError):
    pass


class JsonRpcRequest(object):
    def __init__(self, method=None, params=None, id=None, **kwargs):
        self.method = method
        self.params = params or {}
        self.id = id
        self.extra = kwargs
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
    def from_string(cls, string):
        try:
            return cls.from_dict(json.loads(string))
        except json.JSONDecodeError:
            raise JsonRpcParseError()

    @classmethod
    def from_dict(cls, d):
        """
        Validates a dict instance and transforms it in a :py:class:`gemstone.core.structs.JsonRpcRequest`
        instance

        :param d: The dict instance
        :return: A :py:class:`gemstone.core.structs.JsonRpcRequest` if everything goes well, or None
                 if the validation fails
        """
        for key in ("method", "jsonrpc"):
            if key not in d:
                raise JsonRpcInvalidRequestError()

        # check jsonrpc version
        jsonrpc = d.get("jsonrpc", None)
        if jsonrpc != "2.0":
            raise JsonRpcInvalidRequestError()

        # check method
        method = d.get("method", None)
        if not method:
            raise JsonRpcInvalidRequestError()
        if not isinstance(method, str):
            raise JsonRpcInvalidRequestError()

        # params
        params = d.get("params", {})
        if not isinstance(params, (list, dict)):
            raise JsonRpcInvalidRequestError()

        req_id = d.get("id", None)
        if not isinstance(req_id, (int, str)) and req_id is not None:
            raise JsonRpcInvalidRequestError()

        instance = cls(
            id=req_id,
            method=method,
            params=params,
        )
        return instance

    def is_notification(self):
        return self.id is None

    def __repr__(self):
        return "<JsonRpcRequest id={} method={} params={}>".format(self.id, self.method, self.params)


class JsonRpcResponse(object):
    def __init__(self, result=None, id=None, error=None, send_id_field=False):
        self.response = result
        self.id = id
        self.error = error
        self.send_id_field = send_id_field

    def to_dict(self):
        to_return = {
            "jsonrpc": "2.0",
            "result": self.response,
            "error": self.error,
        }
        if self.id or self.send_id_field:
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


class JsonRpcRequestBatch(object):
    def __init__(self, batch_of_jsonrpc_req):
        """
        Makes a json rpc request batch object from a list of :py:class:`gemstone.core.structs.JSonRpcRequest`
        objects

        :param batch_of_jsonrpc_req: list of :py:class:`gemstone.core.structs.JSonRpcRequest`
        """
        self.items = list(batch_of_jsonrpc_req)

    def add_item(self, item):
        """Adds an item to the batch"""
        self.items.append(item)

    def to_string(self):
        return json.dumps([x.to_string() for x in self.items])

    @classmethod
    def from_json_list(cls, l):
        items = []
        for item_raw in l:
            items.append(JsonRpcRequest.from_dict(item_raw))
        return cls(items)

    def iter_items(self):
        for item in self.items:
            yield item


class JsonRpcResponseBatch(object):
    def __init__(self, batch):
        self.items = batch

    def add_item(self, item):
        """Adds an item to the batch."""

        if not isinstance(item, JsonRpcResponse):
            raise TypeError("Expected JsonRpcResponse but got {} instead".format(type(item).__name__))

        self.items.append(item)

    def iter_items(self):
        for item in self.items:
            yield item

    def to_string(self):
        return json.dumps([i.to_dict() for i in self.iter_items()])


class GenericResponse:
    PARSE_ERROR = JsonRpcResponse(error={"code": -32700, "message": "Parse error"}, send_id_field=True)
    INVALID_REQUEST = JsonRpcResponse(error={"code": -32600, "message": "Invalid Request"}, send_id_field=True)
    METHOD_NOT_FOUND = JsonRpcResponse(error={"code": -32601, "message": "Method not found"})
    INVALID_PARAMS = JsonRpcResponse(error={"code": -32602, "message": "Invalid params"})
    INTERNAL_ERROR = JsonRpcResponse(error={"code": -32603, "message": "Internal error"})
    ACCESS_DENIED = JsonRpcResponse(error={"code": -32001, "message": "Access denied"})

    NOTIFICATION_RESPONSE = JsonRpcResponse()


def parse_json_structure(string_item):
    """
    Given a raw representation of a json structure, returns the parsed corresponding data
    structure (``JsonRpcRequest`` or ``JsonRpcRequestBatch``)

    :param string_item:
    :return:
    """
    if not isinstance(string_item, str):
        raise TypeError("Expected str but got {} instead".format(type(string_item).__name__))

    try:
        item = json.loads(string_item)
    except json.JSONDecodeError:
        raise JsonRpcParseError()

    if isinstance(item, dict):
        return JsonRpcRequest.from_dict(item)
    elif isinstance(item, list):
        if len(item) == 0:
            raise JsonRpcInvalidRequestError()

        request_batch = JsonRpcRequestBatch([])
        for d in item:
            try:
                # handles the case of valid batch but with invalid
                # requests.
                if not isinstance(d, dict):
                    raise JsonRpcInvalidRequestError()
                # is dict, all fine
                parsed_entry = JsonRpcRequest.from_dict(d)
            except JsonRpcInvalidRequestError:
                parsed_entry = GenericResponse.INVALID_REQUEST
            request_batch.add_item(parsed_entry)
        return request_batch
