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

    .. autoattribute:: pymicroservice.PyMicroService.extra_handlers
        :annotation: = A list of tuples of form (url_expression, tornado_handler) that will be added to the default
                Tornado application.

    .. autoattribute:: pymicroservice.PyMicroService.template_dir
        :annotation: = The path of the directory where the default Tornado application will look for templates. To
                read more about how to use templates in Tornado, see http://www.tornadoweb.org/en/stable/template.html

    .. autoattribute:: pymicroservice.PyMicroService.static_dirs
        :annotation: = A list of directory paths in which the default Tornado app will search for static files.


.. autofunction:: pymicroservice.public_method

.. autofunction:: pymicroservice.private_api_method

