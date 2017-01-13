0.1.1 (13.01.2017)
==================

- changed the name of the library from ``pymicroservice`` to ``gemstone``
- added the ``gemstone.MicroService.accessible_at`` attribute

0.1.0 (09.01.2017)
==================

- added the ``pymicroservice.PyMicroService.get_cli`` method
- improved documentation a little bit

0.0.4
=====

- fixed bug when sending a notification that would result in an error 
was causing the microservice to respond abnormally (see #10)
- fixed a bug that was causing the service to never respond with the
invalid parameters status when calling a method with invalid parameters

0.0.3
=====

- added ``pymicroservice.RemoteService`` class
- added the ``pymicroservice.PyMicroService.get_service(name)``
- improved documentation
