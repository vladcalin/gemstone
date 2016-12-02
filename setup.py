import os.path
import re
from setuptools import setup, find_packages


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


module_content = get_file_content(os.path.join("pymicroservice", "__init__.py"))

setup(
    # project metadata
    name="pymicroservice",
    version=get_meta_attr_from_string("__version__", module_content),

    author=get_meta_attr_from_string("__author__", module_content),
    author_email=get_meta_attr_from_string("__email__", module_content),
    description=get_file_content("readme.md"),
    short_description="Build microservices with Python",

    # packages
    packages=find_packages(),
    include_package_data=True,

    # tests
    test_suite="tests",

    install_requires=read_dependencies("requirements.txt"),
    entry_points={
        "console_scripts": [
            "pymicroservice-cli = pymicroservice.cli:main"
        ]
    }
)
