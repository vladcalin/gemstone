import os.path
import re
import sys
from setuptools import setup, find_packages

# Check the Python version. Currently only 3.4+ is supported

if sys.version_info < (3, 4):
    sys.exit("Supported only for Python 3.4 or newer.")


# Utility functions

def read_dependencies(req_file):
    with open(req_file) as req:
        return [line.strip() for line in req]


def get_file_content(filename):
    with open(filename) as f:
        return f.read()


def get_meta_attr_from_string(meta_attr, content):
    result = re.search("{attrname}\s*=\s*['\"]([^'\"]+)['\"]".format(attrname=meta_attr), content)
    if not result:
        raise RuntimeError("Unable to extract {}".format(meta_attr))
    return result.group(1)


# Metadata

CLASSIFIERS = """
    Development Status :: 3 - Alpha
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent
    Topic :: Utilities
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
"""
URL = "https://github.com/vladcalin/gemstone"
KEYWORDS = "microservice service gemstone jsonrpc rpc http asynchronous async tornado asyncio"
DESCRIPTION = "Build microservices with Python"
LICENSE = "MIT"

module_content = get_file_content(os.path.join("gemstone", "__init__.py"))

readme = get_file_content("README.rst")

setup(
    # project metadata
    name="gemstone",
    version=get_meta_attr_from_string("__version__", module_content),
    license=LICENSE,

    author=get_meta_attr_from_string("__author__", module_content),
    author_email=get_meta_attr_from_string("__email__", module_content),

    maintainer=get_meta_attr_from_string("__author__", module_content),
    maintainer_email=get_meta_attr_from_string("__email__", module_content),

    long_description=readme,
    description=DESCRIPTION,
    keywords=KEYWORDS.split(),
    classifiers=[x.strip() for x in CLASSIFIERS.split("\n") if x != ""],
    url=URL,

    zip_safe=False,

    # packages
    packages=find_packages(),
    include_package_data=True,

    # tests
    test_suite="tests",
    test_requires="pytest",

    install_requires=[
        "tornado",
        "simplejson",
        "click"
    ],

    entry_points={
        "console_scripts": [
            "gemstone = gemstone.cli:cli"
        ]
    },
    extras_requires={
        "events-rabbitmq": ["pika"],
        "discover-redis": ["redis"],
        "discover-etcd": ["python-etcd"]
    }
)
