from setuptools import setup, find_packages


def read_dependencies(req_file):
    with open(req_file) as req:
        return [line.strip() for line in req]


def get_file_content(filename):
    with open(filename) as f:
        return f.read()


setup(
    name="pymicroservice",
    version="0.0.1",
    description=get_file_content("readme.md"),
    short_description="Build microservices with Python",

    packages=find_packages(),
    include_package_data=True,

    install_requires=read_dependencies("requirements.txt"),
    entry_points={
        "console_scripts": [
            "pymicroservice-cli = pymicroservice.cli:main"
        ]
    }
)
