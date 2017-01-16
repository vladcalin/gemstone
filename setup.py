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


module_content = get_file_content(os.path.join("gemstone", "__init__.py"))

readme = get_file_content("README.rst")
history = get_file_content("CHANGES.rst")

setup(
    # project metadata
    name="gemstone",
    version=get_meta_attr_from_string("__version__", module_content),
    license="MIT",

    author=get_meta_attr_from_string("__author__", module_content),
    author_email=get_meta_attr_from_string("__email__", module_content),

    maintainer=get_meta_attr_from_string("__author__", module_content),
    maintainer_email=get_meta_attr_from_string("__email__", module_content),

    long_description=readme + "\n\n" + history,
    description="Build microservices with Python",
    keywords=["microservice", "cloud", "rpc", "compute", "service"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries"
    ],
    url="https://github.com/vladcalin/gemstone",

    zip_safe=False,

    # packages
    packages=find_packages(),
    include_package_data=True,

    # tests
    test_suite="tests",

    install_requires=read_dependencies("requirements.txt")
)
