import os
import pkg_resources

import click

import gemstone.data


@click.group()
def cli():
    pass


@cli.command()
@click.argument("classname", required=True)
@click.argument("filename", required=True)
def new_service(classname, filename):
    template = os.path.join(os.path.dirname(os.path.abspath(gemstone.data.__file__)), "newservice.tmpl")
    with open(template, "r") as tmpl, open(filename, "w") as output:
        output.write(tmpl.read() % {"classname": classname})


def main():
    cli()
