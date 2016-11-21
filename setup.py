from setuptools import setup, find_packages

setup(
    name="pymicroservice",
    version="0.0.1",
    description="Build microservices with Python",
    packages=find_packages(),
    extras_require={
        "flask": ["flask"]
    },
    entry_points={
        "console_scripts": [
            "pymicroservice_builtin = pymicroservice.builtin.cli:main"
        ]
    }
)
