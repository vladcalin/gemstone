import pprint
import time
import click

from gemstone import RemoteService


def format_params(params):
    parameters = {}
    for pair in params:
        k, *v = pair.split("=")
        parameters[k] = "=".join(v)
    return parameters


@click.group()
def cli():
    pass


@cli.command("call")
@click.option("--registry", help="The service registry URL used for queries")
@click.argument("name")
@click.argument("method")
@click.argument("params", nargs=-1)
def call(registry, name, method, params):
    # TODO add proper validation and fail messages so that the user knows what is going on
    _start = time.time()
    service = RemoteService.get_service_by_name(registry, name)
    print("[!] Service identification: {:.5f} seconds".format(time.time() - _start))
    print("[!] Service name: {}".format(service.name))
    print("[!] Service URL : {}".format(service.url))

    parameters = format_params(params)

    _start = time.time()
    result = getattr(service.methods, method)(**parameters)
    print("[!] Method call: {:.5f} seconds".format(time.time() - _start))
    print("[!] Result:\n")
    pprint.pprint(result)


@cli.command("call_raw")
@click.argument("url")
@click.argument("method")
@click.argument("params", nargs=-1)
def call_raw(url, method, params):
    _start = time.time()
    service = RemoteService(url)
    print("[!] Service identification: {:.5f} seconds".format(time.time() - _start))
    parameters = format_params(params)

    _start = time.time()
    result = getattr(service.methods, method)(**parameters)
    print("[!] Method call: {:.5f} seconds".format(time.time() - _start))

    print("[!] Result:\n")
    pprint.pprint(result)
