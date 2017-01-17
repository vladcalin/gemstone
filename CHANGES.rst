0.2.0 (17.01.2017)
~~~~~~~~~~~~~~~~~~

- added ``gemstone.RemoteService.get_service_by_name`` method
- added ``call`` command to cli
- added ``call_raw`` command to cli
- improved documentation a little

0.1.3 (16.01.2017)
~~~~~~~~~~~~~~~~~~

- fixed manifest to include required missing files

0.1.2 (16.01.2017)
~~~~~~~~~~~~~~~~~~

- added py36 to travis-ci
- refactored setup.py and reworked description files and documentation for better rendering

0.1.1 (13.01.2017)
~~~~~~~~~~~~~~~~~~

- changed the name of the library from ``pymicroservice`` to ``gemstone``
- added the ``gemstone.MicroService.accessible_at`` attribute

0.1.0 (09.01.2017)
~~~~~~~~~~~~~~~~~~

- added the ``pymicroservice.PyMicroService.get_cli`` method
- improved documentation a little bit

0.0.4
~~~~~

- fixed bug when sending a notification that would result in an error 
  was causing the microservice to respond abnormally (see #10)
- fixed a bug that was causing the service to never respond with the
  invalid parameters status when calling a method with invalid parameters

0.0.3
~~~~~

- added ``pymicroservice.RemoteService`` class
- added the ``pymicroservice.PyMicroService.get_service(name)``
- improved documentation
