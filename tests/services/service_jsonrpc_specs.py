from gemstone import MicroService, public_method, private_api_method


class ServiceJsonRpcSpecs(MicroService):
    name = "test.service"

    host = "127.0.0.1"
    port = 9999

    skip_configuration = True

    @public_method
    def test_method_no_params(self):
        return "success_1"

    @public_method
    def test_method_params(self, param1, param2):
        return "this {} is a {}".format(param1, param2)

    @public_method
    def test_method_var_params(self, **kwargs):
        return {
            "kwargs": kwargs
        }

    @private_api_method
    def test_method_priv_no_params(self):
        pass

    def api_token_is_valid(self, api_token):
        return api_token == "test-token"
