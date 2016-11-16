The **pymicroservice** framework
================================

Motivation
----------

In the past years, the microservice-based architecture became very popular in the computing field. 
Although this architecture grew more and more popular, there are a few tools that can help an
individual to build such systems. The current alternatives are using [nameko](https://github.com/nameko/nameko) 
or by building a web application that acts like a microservice. I started developing this framework in order
to provide a tool for creating and managing such systems with ease, and that are capable of being specialized in
a certain role, be it entity management, data storage or just computing.

What I want to accomplish
-------------------------

I want to obtain a framework that will allow someone to develop a microservice in a manner similat to this
```python

	from pymicroservice.core import PyMicroService
	from pymicroservice.gw_adapters import HttpGatewayAdapter, BinaryStreamGatewayAdapter
	from pymicroservice.constants import HTTP_JSON, HTTP_REST

	class MyMicroservice(PyMicroService):

		name = "test.microservice.basic"

		database = create_database("mongodb://127.0.0.1:27017")
		process_worker_pool = ProcessWorkerPool(worker_count=5, threads_per_worker=5)
		thread_worker_pool = ThreadWorkerPool(worker_count=5)

		@http_endpoint("POST")
		@async_http_endpoint("POST")
		def compute_stuff(self, job_name):
			pass

		@http_endpoint("POST")
		@async_http_endpoint("POST")
		def store_data(self, entity_name, entity_data):
			pass

		@http_endpoint("GET")
		def get_stored_data(self, entity_name):
			pass

	if __name__ == '__main__':
		microservice = MyMicroservice(("0.0.0.0", 5533))

		# register with the ServiceIdentifierService at http://svc-identify.myserver.com:80/ 
		# so that other services can easily locate it
		microservice.set_identifier_database(("svc-identify.myserver.com", 80))

		microservice.add_gateway_adapter(HttpGatewayAdapter(HTTP_JSON_RPC))
		microservice.add_gateway_adapter(HttpGatewayAdapter(HTTP_REST))
		microservice.add_gateway_adapter(BinaryStreamGatewayAdapter())

		microservice.serve()
		# Spawining workers...
		# Spawining worker threads...
		# Spawining HttpGatewayAdapter with HTTP_JSON_RPC...
		#     Listening on http://0.0.0.0/api/json_rpc
		# Spawining HttpGatewayAdapter with HTTP_REST...
		# 	  Listening on http://0.0.0.0/api/rest
		# Spawining BinaryStreamGatewayAdapter...
		# 	  Listening on socket://0.0.0.0

```

And maybe a tool for easily generating documentation for the APIs

```python

	from pymicroservice.utils.docs import generate_documentation

	generate_documentation(MyMicroservice, HttpGatewayAdapter(HTTP_JSON_RPC), "docs/html")
	# Generating documentation for endpoint /api/json_rpc
	# Generating documentation for endpoint /api/json_rpc/compute_stuff
	# Generating documentation for endpoint /api/json_rpc/compute_stuff/async
	# Generating documentation for endpoint /api/json_rpc/store_data
	# Generating documentation for endpoint /api/json_rpc/store_data/async
	# Generating documentation for endpoint /api/json_rpc/get_stored_data
	# Done.
	# Documentation generated in 

```

Project status
--------------

This project is under heavy development.