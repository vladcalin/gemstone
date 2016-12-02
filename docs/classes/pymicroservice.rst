pymicroservice.PyMicroService
=============================


.. autoclass:: pymicroservice.PyMicroService
    :members:

    .. autoattribute:: pymicroservice.PyMicroService.name
        :annotation: = a string representing the name of the service. MUST be specified by user

    .. autoattribute:: pymicroservice.PyMicroService.host
        :annotation: = a string representing the address or host to bind. Defaults to 127.0.0.1

    .. autoattribute:: pymicroservice.PyMicroService.port
        :annotation: = an integer representing the port to bind. Defaults to 8000

    .. autoattribute:: pymicroservice.PyMicroService.max_parallel_blocking_tasks
        :annotation: = an integer representing how many parallel tasks can be executed in parallel. Defaults to os.cpu_count()

    .. autoattribute:: pymicroservice.PyMicroService.api_token_header
        :annotation: = a string representing what HTTP header will contain the API token based on which access to the
                private methods will be granted (or not).

    .. automethod:: pymicroservice.PyMicroService.api_token_is_valid


.. autofunction:: pymicroservice.public_method

.. autofunction:: pymicroservice.private_api_method

