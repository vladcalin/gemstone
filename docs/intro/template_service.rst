Using a template for writing a microservice
===========================================

There is the `gemstone-template <https://github.com/vladcalin/gemstone-template>`_ cookiecutter template
for easily setting up a microservice. Check out its readme for more info.

Quick usage
-----------

::

    pip install cookiecutter gemstone
    git clone https://github.com/vladcalin/gemstone-template.git
    cookiecutter ./gemstone-template

    # answer the questions
    # Name: myservice
    # Author: Me
    # Version: 1.0
    # Short description: None

    # Now we have the myservice directory with the new service

    pip install myservice
    myservice start --host=0.0.0.0 --port=8000

    # now our first service is up and running

    # the service logic is in myservice/service.py
    # if you want to create extra handlers (for a web interface for example)
    #   add them to myservice/handlers
    # static files are in myservice/html/static
    # templates are in myservice/html/templates

Enjoy!