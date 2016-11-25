Introduction
============

What are microservices
----------------------

Nowadays, from the need of building a highly scalable application
that is fast to deploy, scale and update, there appeared a new architectural
pattern: microservices.

Instead of building an application as a multi-layered monolithic piece of software,
there is the alternative to split that system into multiple independent components (services)
that communicate with each other.

This new architectural pattern has some advantages:

- **Ease of development**: the developers don't need to work on the same codebase and are not limited
    to a single language: microservices can be written in different languages and using different
    technology stacks. Think of microservices as stand alone applications that interact with each other in
    order to form a system.
- **Highly scalable**: nowadays the CPUs reached their maximum performance peak and it is basically
    impossible to scale vertically anymore (by running the application on a powerful and expensive machine) for
    much longer and by using microservices, the application can scale easily horizontally by deploying multiple
    instances of each service and balancing loads between them.
- **High availability** because by running multiple instances of each service on multiple nodes that
    run individually, we can avoid the one point of failure
    situation in the situation of an unavoidable failure (be it hardware or software).